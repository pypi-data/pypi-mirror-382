from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import *
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import lit, col as col_, sum as sum_, when

from dasl_client.preset_development.preview_parameters import *
from dasl_client.preset_development.stage import *
from dasl_client.preset_development.errors import *

import yaml
import os
from itertools import count

from IPython import get_ipython


@udf(StringType())
def constant_udf(*args):
    return "<sortable_random_id>"


class PreviewEngine:
    """
    This class deserializes the in-development preset's YAML and performs a series of
    validation steps before attempting to compile each stage's table and execute them
    based on the provided PreviewParameters.

    Upon successful execution, output is generated for each successfully executed
    stage's table operations. Additionally, if Gold stages are computed, their outputs
    are validated against the provided Gold stage tables to ensure compatibility on a
    per-table-name basis with the Unity Catalog.

    For example, a preset Gold stage table named "http_activity" will be checked against
    the corresponding table in the Unity Catalog schema—also named "http_activity" to
    confirm that inserting into the Unity Catalog most likely not cause errors.
    """

    def __init__(
        self, spark: SparkSession, preset_yaml_str: str, ds_params: PreviewParameters
    ):
        """
        Creates the PreviewEngine using the given preset YAML and datasource parameters.
        The YAML is deserialized here and checked to verify whether the requested
        pretransform name, if provided, exists in the preset.

        Instance Attributes:
            ds_params (PreviewParameters): The input datasource's configuration.
            preset (Dict[str, Any]): The deserialized preset YAML.
            pretransform_name (str): The name of the requested pretransform. Defaults to None.
            pre (Stage): Stores the pretransform Stage object internally.
            silver (List[Stage]): Stores the Silver Stage objects internally.
            gold (List[Stage]): Stores the Gold Stage objects internally.
        """
        self._spark = spark
        self._ds_params = ds_params
        self.__stage_exception = {}
        self._preset = yaml.safe_load(preset_yaml_str)
        self._pretransform_name = ds_params._pretransform_name

        self._validate_gold_inputs(
            self._preset.get("silver", None), self._preset.get("gold", None)
        )
        if self._pretransform_name:
            self._validate_pretransform_name(
                self._preset.get("silver", None), self._pretransform_name
            )

        self._pre_bronze = None
        self._bronze = None
        self._pre_silver = None
        self._silver = []
        self._gold = []
        self._result_df_map: Tuple[
            DataFrame, Dict[str, DataFrame], Dict[str, DataFrame]
        ] = (None, {}, {})

    def _validate_pretransform_name(
        self, silver: Dict[str, str], pretransform_name: str
    ) -> None:
        """
        Validates the given pretransform name exists in the provided preset's Silver
        PreTransform stages.
        """
        if not silver:
            raise NoSilverStageProvdedError(", but pretransform name provided")
        if not (silver_pre_transform := silver.get("preTransform", None)):
            raise NoSilverPreTransformStageProvdedError()
        silver_pre_output_names = []
        for table in silver_pre_transform:
            if not (name := table.get("name", None)):
                raise MissingTableFieldError(
                    "Silver pretransform",
                    table.get("name", "<stage missing name>"),
                    "name",
                )
            silver_pre_output_names += [name]
        if pretransform_name not in silver_pre_output_names:
            raise PreTransformNotFound()

    def _validate_gold_inputs(
        self, silver: Dict[str, str], gold: Dict[str, str]
    ) -> None:
        """
        Validate gold tables all have a silver table to input from.
        """
        if not gold:
            return

        if not len(gold):
            return

        if not silver:
            raise NoSilverStageProvdedError(", but gold stage is present")

        gold_input_names = []
        for table in gold:
            if not (input := table.get("input", None)):
                raise MissingTableFieldError(
                    "Gold", table.get("name", "<stage missing name>"), "input"
                )
            gold_input_names += [input]

        if not (silver_transform := silver.get("transform", None)):
            raise NoSilverTransformStageProvdedError()
        silver_output_names = []
        for table in silver_transform:
            if not (name := table.get("name", None)):
                raise MissingTableFieldError(
                    "Silver transform", table.get("name", ""), "name"
                )
            silver_output_names += [name]

        missing_keys = set(gold_input_names) - set(silver_output_names)
        if missing_keys:
            raise MissingSilverKeysError(missing_keys)

    def _compile_stages(self, force_evaluation: bool = False) -> None:
        """
        Creates Stage objects, setting silver pretransform to None if not provided.
        """
        pre_bronze_field_counter = count()
        pre_bronze_name_counter = count()
        pre_bronze_expr_groups = self._preset.get("bronze", {}).get("preTransform", [])
        if pre_bronze_expr_groups:
            tables = [
                {
                    "name": f"Index {next(pre_bronze_name_counter)}",
                    "fields": [
                        {"name": str(next(pre_bronze_field_counter)), "expr": expr}
                        for expr in expr_group
                    ],
                }
                for expr_group in pre_bronze_expr_groups
            ]
            for table in tables:
                self._pre_bronze = [
                    Stage(self._spark, "bronze pretransform", table) for table in tables
                ]

        pretransform = None
        if self._pretransform_name:
            for table in self._preset["silver"]["preTransform"]:
                if table["name"] == self._pretransform_name:
                    self._pre_silver = Stage(self._spark, "silver pretransform", table)
                    break

        self._silver = [
            Stage(
                self._spark,
                "silver transform",
                table,
                force_evaluation=force_evaluation,
            )
            for table in self._preset.get("silver", {}).get("transform", [])
        ]
        self._gold = [
            Stage(self._spark, "gold", table, force_evaluation=force_evaluation)
            for table in self._preset.get("gold", [])
        ]

    def _run(
        self, df: DataFrame, verbose: bool = False
    ) -> Tuple[DataFrame, Dict[str, DataFrame], Dict[str, DataFrame]]:
        """
        Runs all stages, in medallion stage order. This allows prior stage outputs to feed
        into later stage inputs.

        Returns:
            Dataframes containing the output from each run Stage.
        """
        # If we are in silverbronze mode, and an autoloader has been provided, or we are
        # not in silverbronze mode, we need to run the preBronze stage.
        pre_bronze_output = {}
        if (
            self._ds_params._mode != "silverbronze"
            or self._ds_params._autoloader_location
        ):
            if self._pre_bronze:
                for stage in self._pre_bronze:
                    df = stage.run(df)
                    pre_bronze_output[stage._name] = df
        else:
            # We are in silverbronze mode with no autoloader, so we treat first
            # silverbronze table as initial df.
            df = (
                self._spark.table(self._ds_params._bronze_tables[0].get("name", ""))
                .drop("dasl_id")
                .limit(self._ds_params._record_limit)
            )

        if time_col := self._ds_params._time_column:
            df = df.filter(
                f"timestamp({time_col}) >= timestamp('{self._ds_params._start_time}') AND timestamp({time_col}) < timestamp('{self._ds_params._end_time}')"
            )

        df = df.withColumn("dasl_id", constant_udf())

        self._bronze = df

        # Deal with silverbronze table joins.
        # Note: We can blind get here as validation should've caught anything missing.
        if self._ds_params._mode == "silverbronze":
            if alias := self._ds_params._bronze_tables[0].get("alias", None):
                df = df.alias(alias)
            for bronze_table in self._ds_params._bronze_tables[1:]:
                join_df = (
                    spark.table(bronze_table["name"])
                    .drop("dasl_id")
                    .limit(self._ds_params._record_limit)
                )
                if alias := bronze_table.get("alias", None):
                    join_df = join_df.alias(alias)
                df = df.join(
                    join_df,
                    expr(bronze_table["joinExpr"]),
                    bronze_table.get("joinType", "left"),
                )

        if self._pre_silver:
            df = self._pre_silver.run(df)

        silver_output_map = {}
        for table in self._silver:
            silver_output_map[table._name] = table.run(df)

        # Check for silver stage exceptions.
        # NOTE: These exception lists only get populated if force_evaluation is enabled.
        for table in self._silver:
            if exceptions := table.get_exceptions():
                self.__stage_exception[table._name] = exceptions
        if self.__stage_exception:
            raise StageExecutionException("silver", self.__stage_exception, verbose)

        gold_output_map = {}
        for table in self._gold:
            # We store as gold_name/silver_input to prevent clobbering on duplicate gold table use.
            gold_output_map[f"{table._name}/{table._input}"] = table.run(
                silver_output_map[table._input]
            )

        # Check for gold stage exceptions.
        # NOTE: These exception lists only get populated if force_evaluation is enabled.
        for table in self._gold:
            if exceptions := table.get_exceptions():
                self.__stage_exception[table._name] = exceptions
        if self.__stage_exception:
            raise StageExecutionException("gold", self.__stage_exception, verbose)

        return (
            (df, silver_output_map, gold_output_map, pre_bronze_output)
            if self._pre_silver
            else (None, silver_output_map, gold_output_map, pre_bronze_output)
        )

    def __get_sql_type(self, data_type) -> str:
        """
        Helper to convert Spark data type objects to SQL type strings.
        """
        if isinstance(data_type, StringType):
            return "STRING"
        elif isinstance(data_type, IntegerType):
            return "INT"
        elif isinstance(data_type, LongType):
            return "BIGINT"
        elif isinstance(data_type, FloatType):
            return "FLOAT"
        elif isinstance(data_type, DoubleType):
            return "DOUBLE"
        elif isinstance(data_type, BooleanType):
            return "BOOLEAN"
        elif isinstance(data_type, TimestampType):
            return "TIMESTAMP"
        elif isinstance(data_type, DateType):
            return "DATE"
        elif isinstance(data_type, ArrayType):
            return f"ARRAY<{self.__get_sql_type(data_type.elementType)}>"
        elif isinstance(data_type, MapType):
            return f"MAP<{self.__get_sql_type(data_type.keyType)}, {self.__get_sql_type(data_type.valueType)}>"
        elif isinstance(data_type, StructType):
            fields = ", ".join(
                [
                    f"{field.name}: {self.__get_sql_type(field.dataType)}"
                    for field in data_type.fields
                ]
            )
            return f"STRUCT<{fields}>"
        elif isinstance(data_type, VariantType):
            return f"VARIANT"
        else:
            return f"UNKNOWN ({data_type})"

    def __format_gold_column_merge_exception(
        self,
        columns: Dict[str, List[Exception]],
        gold_df: DataFrame,
        verbose: bool = False,
    ):
        """
        Formatter for various exceptions that occur during the merge of gold tables.
        """
        missing_column_flag = False
        for column, info in columns.items():
            # RANT: it is annoying, but basically every exception comes back from the
            # query analyzer as pyspark.errors.exceptions.connect.AnalysisException,
            # so we are forced into this awkward string search.
            str_e = str(info["exception"])
            str_e = str_e.split("JVM")[0] if not verbose else str_e
            if "LEGACY_ERROR_TEMP_DELTA_0007" in str_e:
                print(
                    f"-> Column \"{column}\" of type \"{self.__get_sql_type(info['type'])}\" does not exist in gold table \"{info['table']}\"."
                )
                missing_column_flag = True
            elif "DELTA_FAILED_TO_MERGE_FIELDS" in str_e:
                print(
                    f"-> Column \"{column}\" of type \"{self.__get_sql_type(info['type'])}\" is not compatiable with gold table \"{info['table']}\"'s \"{column}\" of type \"{self.__get_sql_type(gold_df.schema[column].dataType)}\""
                )
            else:
                print(
                    f"-> Column \"{column}\" raised the following unformatted exception when appending to gold table \"{info['table']}\":\n{str_e}"
                )

        if missing_column_flag:
            print(
                f"\nA write to 1 or more non-existent columns occured - available columns are: {', '.join(gold_df.columns)}"
            )

    def _render_output(
        self,
        input_df: DataFrame,
        stage_dataframes: Tuple[
            List[DataFrame], DataFrame, Dict[str, DataFrame], Dict[str, DataFrame]
        ],
        gold_table_catalog: str,
        gold_table_schema: str,
        verbose: bool = False,
    ) -> None:
        """
        Displays formatted HTML output from executed Stages' DataFrames.
        """
        # TODO: Investigate further into using Databricks's style sheets here.

        # Get the Databricks built-in functions out the namespace.
        ipython = get_ipython()
        if ipython is not None:
            displayHTML = ipython.user_ns["displayHTML"]
            display = ipython.user_ns["display"]
        else:
            displayHTML = lambda x: print(x)
            display = lambda x, **kwargs: x.show()

        def d(txt, lvl) -> None:
            displayHTML(
                f"""
                <div style="background-color:
                background-color: rgb(18, 23, 26); padding: 0; margin: 0;">
                    <h{lvl} style="margin: 0; background-color: rgb(244, 234, 229);">{txt}</h{lvl}>
                </div>
                """
            )

        (pre_silver, silver, gold, pre_bronze) = stage_dataframes
        d("Autoloader Input", 1)
        display(
            input_df,
            checkpointLocation=os.path.join(
                self._ds_params.get_checkpoint_temp_location(), "input"
            ),
        )
        d("Bronze Pre-Transform", 1)
        for name, df in pre_bronze.items():
            d(f"{name}", 2)
            display(
                df,
                checkpointLocation=os.path.join(
                    self._ds_params.get_checkpoint_temp_location(), f"pre_bronze-{name}"
                ),
            )
        d("Silver Pre-Transform", 1)
        if pre_silver:
            display(
                pre_silver,
                checkpointLocation=os.path.join(
                    self._ds_params.get_checkpoint_temp_location(), "pre_silver"
                ),
            )
        else:
            d("Skipped", 2)
        d("Silver Transform", 1)
        for name, df in silver.items():
            d(f"{name}", 2)
            display(
                df,
                checkpointLocation=os.path.join(
                    self._ds_params.get_checkpoint_temp_location(), f"silver-{name}"
                ),
            )
        d("Gold", 1)
        for full_name, df in gold.items():
            d(f"{full_name}", 2)
            d("Stage output", 3)
            display(
                df,
                checkpointLocation=os.path.join(
                    self._ds_params.get_checkpoint_temp_location(), f"gold-{full_name}"
                ),
            )

            # NOTE: Name is stored as Gold_name/Silver_input. So we need to get just the Gold table
            # name that we are comparing the dataframe metadata to.
            name = full_name.split("/")[0]
            fqn_gold_table_name = f"{self.force_apply_backticks(gold_table_catalog)}.{self.force_apply_backticks(gold_table_schema)}.{self.force_apply_backticks(name)}"

            if not self._spark.catalog.tableExists(f"{fqn_gold_table_name}"):
                raise UnknownGoldTableError(name, gold_table_schema)

            # Create a temporary table to perform the type check
            delta_df = self._spark.table(f"{fqn_gold_table_name}").limit(0)
            delta_df.write.mode("overwrite").save(
                f"{self._ds_params.get_autoloader_temp_schema_location()}/{full_name}"
            )

            # Update the params to indicate we've added a testing temp gold table
            self._ds_params.add_gold_schema_table(full_name)

            # Perform the type checks by trying to insert data into the table

            df_columns = df.columns
            df_single_columns = {}
            df_append_exceptions = {}
            for column in df_columns:
                df_single_columns[column] = df.select(column)
            for column, df_single_column in df_single_columns.items():
                try:
                    df_single_column.write.mode("append").save(
                        f"{self._ds_params.get_autoloader_temp_schema_location()}/{full_name}"
                    )
                except Exception as e:
                    df_append_exceptions[column] = {
                        "type": df_single_column.schema[column].dataType,
                        "exception": e,
                        "table": name,
                    }

            self.__format_gold_column_merge_exception(
                df_append_exceptions, delta_df, verbose
            )

            if not df_append_exceptions:
                # alls good. display the output.
                d("Resultant gold table preview", 3)
                unioned_df = delta_df.unionByName(df, allowMissingColumns=True)
                display(
                    unioned_df,
                    checkpointLocation=os.path.join(
                        self._ds_params.get_checkpoint_temp_location(),
                        f"gold-unioned-{full_name}",
                    ),
                )

    def is_backtick_escaped(self, name: str) -> bool:
        """
        check if a given (column) name is backtick escaped or not
        :param name: column name
        :return: bool
        """
        return name.startswith("`") and name.endswith("`")

    def force_apply_backticks(self, name: str) -> str:
        """
        forces application of backticks to the given (column) name as a single unit
        if it already has backticks this is a noop
        :param name: column name
        :return: str
        """
        if self.is_backtick_escaped(name):
            return name
        return f"`{name}`"

    def evaluate(
        self,
        gold_table_schema: str,
        display: bool = True,
        force_evaluation: bool = False,
        verbose: bool = False,
    ) -> None:
        """
        Evaluates the loaded preset YAML using the input datasource configuration to load
        records. Finally, checks that the output from the Gold stages is compatible with
        the Unity Catalog Gold tables.
        """
        s = gold_table_schema.split(".")
        if len(s) != 2:
            raise InvalidGoldTableSchemaError(gold_table_schema)
        catalog_name = s[0].lstrip("`").rstrip("`")
        schema_name = s[1].lstrip("`").rstrip("`")
        if any(
            row.catalog == catalog_name
            for row in self._spark.sql("SHOW CATALOGS").collect()
        ):
            if not any(
                row.databaseName == schema_name
                for row in self._spark.sql(
                    f"SHOW SCHEMAS IN `{catalog_name}`"
                ).collect()
            ):
                raise InvalidGoldTableSchemaError(
                    gold_table_schema,
                    f"Schema {schema_name} not found in catalog {catalog_name} or insufficient permissions.",
                )
        else:
            raise InvalidGoldTableSchemaError(
                gold_table_schema,
                f"Catalog {catalog_name} not found or insufficient permissions.",
            )

        # If we are using the autoloader, fetch format from preset and others.
        if self._ds_params._mode == "autoloader" or (
            self._ds_params._mode == "silverbronze"
            and self._ds_params._autoloader_location
        ):
            if self._preset.get("bronze", {}).get("loadAsSingleVariant", False) == True:
                self._ds_params._set_load_as_single_variant()
            if not (autoloader_conf := self._preset.get("autoloader", None)):
                raise MissingAutoloaderConfigError()
            if not (file_format := autoloader_conf.get("format", None)):
                raise AutoloaderMissingFieldError("format")
            self._ds_params._set_autoloader_format(file_format)
            if schemaFile := autoloader_conf.get("schemaFile", None):
                self._ds_params._set_autoloader_schema_file(schemaFile)
            if cloudFiles := autoloader_conf.get("cloudFiles", None):
                if schema_hints := cloudFiles.get("schemaHints", None):
                    self._ds_params._set_autoloader_cloudfiles_schema_hints(
                        schema_hints
                    )
                if schema_hints_file := cloudFiles.get("schemaHintsFile", None):
                    self._ds_params._set_autoloader_cloudfiles_schema_hint_file(
                        schema_hints_file
                    )

        self._compile_stages(force_evaluation=force_evaluation)

        with self._ds_params as df:
            self._result_df_map = self._run(df, verbose)
            if display:
                self._render_output(
                    df,
                    self._result_df_map,
                    self.force_apply_backticks(catalog_name),
                    self.force_apply_backticks(schema_name),
                    verbose,
                )

    def results(
        self,
    ) -> Tuple[DataFrame, DataFrame, Dict[str, DataFrame], Dict[str, DataFrame]]:
        return self._bronze, *self._result_df_map
