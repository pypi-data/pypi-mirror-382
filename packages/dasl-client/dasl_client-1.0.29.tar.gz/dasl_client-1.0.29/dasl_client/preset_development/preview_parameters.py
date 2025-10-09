from typing import Optional, TYPE_CHECKING

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import *
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import col, lit, udf
from dasl_client.preset_development.errors import *

import uuid
import os

from IPython import get_ipython

if TYPE_CHECKING:
    from dasl_client import Client


class PreviewParameters:
    """
    This class provides three methods for supplying input records to the preset development environment.

    **1. Input Mode:**
    In "input" mode, the user provides the schema and data directly using `StructType`, `StructField`,
    and a list of tuples representing the data. For example:

    ```python
    schema = StructType([
        StructField('name', StringType(), True),
        StructField('age', IntegerType(), True)
    ])

    data = [("Mikhail", 15), ("Zaky", 13), ("Zoya", 8)]

    data_source = PreviewParameters() \
        .from_input() \
        .set_data_schema(schema) \
        .set_data(data)
    ```

    **2. Autoloader Mode:**
    In "autoloader" mode, input is loaded using the `cloudFiles` format and settings defined in the preset's
    `autoloader` field. The format is fetched directly from the preset, while other required options must be
    provided manually. Example:

    ```python
    ds_params = PreviewParameters() \
        .from_autoloader() \
        .set_autoloader_location("s3://test-databucket/test-data") \
        .set_pretransform_name("name_of_pretransform") \
        .set_date_range("EdgeStartTimestamp", "2024-02-15 11:27:21", "2024-02-15 11:27:25")
    ```

    If you wish to skip the Silver PreTransform stage, simply omit the `pretransform_name` setting.

    **3. Table Mode:**
    This method reads input directly from a table:

    ```python
    ds_params = DataSourceParameters(spark) \
        .from_table() \
        .set_table("system.access.audit")
    ```

    **4. SilverBronze Mode:**
    "silverbronze" mode, works like a more advanced "table" mode. It allows for joining of multiple
    tables as input. This mode requires setting bronze table definitions. This mode behaves in 2
    seperate ways depending on whether an autoloader location is set or not. If an autoloader location
    is set the first entry in the bronze table definitions is used to name and alias the autoloader's
    input and these can be used in later join expressions. Used in this way, the autoloader will be
    loaded as in "autoloader" mode, and run through preBronze stages before being joined with the
    remainder of the bronze table definitions. This mimics not skipping bronze in a DataSource and
    joining what was read in silver. If an autoloader location is not set, the behaviour instead
    attempts to emulate a DataSource set to skip the bronze stage. That is, all preBronze and bronze
    stages will be skipped, and the name of the first entry in the given bronze table definitions will
    be read from instead. Any subsequent bronze table definitions will be joined against this table.

    Using no autoloader location (this will read from the first table):
    ```python
    bronze_tables = [
    {
        "name": "databricks_dev.default.sev_map",
        "alias": "tab1"
    },
    {
        "name": "databricks_dev.alan_bronze.akamai_waf",
        "alias": "tab2",
        "joinExpr": "id::string = tab2.serviceID",
        "joinType": "left"
    },
    {
        "name": "databricks_dev.alan_silver.cloudflare_hjttp_request",
        "alias": "tab3",
        "joinExpr": "tab1.id::string = tab3.ClientRequestsBytes",
        "joinType": "inner"
    }
    ]

    ds_params = (
        PreviewParameters(spark)
        .from_silverbronze_tables()
        .set_bronze_table_definitions(bronze_tables)
    )

    ps = PreviewEngine(spark, yaml_string, ds_params)
    ps.evaluate("stage.gold")
    ```

    Using an autoloader location (this will read from the autoloader and name the df tab1):
    ```python
    bronze_tables = [
    {
        "name": "tab1"
    },
    {
        "name": "databricks_dev.alan_bronze.akamai_waf",
        "alias": "tab2",
        "joinExpr": "id::string = tab2.serviceID",
        "joinType": "left"
    },
    {
        "name": "databricks_dev.alan_silver.cloudflare_hjttp_request",
        "alias": "tab3",
        "joinExpr": "tab1.id::string = tab3.ClientRequestsBytes",
        "joinType": "inner"
    }
    ]

    ds_params = (
        PreviewParameters(spark)
        .from_silverbronze_tables()
        .set_bronze_table_definitions(bronze_tables)
        .set_autoloader_location("s3://antimatter-dasl-testing/csamples3/mars/area1/")
    )
    ```

    **Note:**
    When using autoloader mode, this implementation requires locations to store temporary schemas and
    checkpoints. By default, these paths are automatically determined from your workspace's
    `daslStoragePath` configuration:
    - Schema location: `{daslStoragePath}/preset_preview/schemas`
    - Checkpoint location: `{daslStoragePath}/preset_preview/checkpoints`

    The workspace configuration is retrieved automatically via `Client.for_workspace()`. If you need
    to use custom paths or don't have access to the DASL API, you can set them explicitly:
    ```python
    ds_params = (PreviewParameters(spark)
        .set_autoloader_temp_schema_location('/Volumes/catalog/schema/volume/schemas')
        .set_checkpoint_temp_location_base('/Volumes/catalog/schema/volume/checkpoints'))
    ```

    Regardless of the paths used, you must have write permissions for those locations.
    """

    def __init__(self, spark: SparkSession, client: Optional["Client"] = None) -> None:
        """
        Initializes the PreviewParameters instance with sparse default settings.

        Note: The preset development environment is intended to process only a small number
        of records at a time. By default, the record limit is set to 10, but this can be overridden
        if needed.

        Args:
            spark: SparkSession for DataFrame operations.
            client: Optional DASL client for retrieving workspace configuration.
                If not provided and storage paths are not set explicitly,
                a client will be created automatically via Client.for_workspace().

        Instance Attributes:
            mode (str): Indicates the source type ("input" or "autoloader").
            record_limit (int): Maximum number of records to load. Defaults to 10.
            autoloader_temp_schema_location (str): Temporary location to store the autoloader schema.
                Defaults to {daslStoragePath}/preset_preview/schemas.
            checkpoint_temp_location_base (str): Temporary location to store checkpoints for stream and display.
                Defaults to {daslStoragePath}/preset_preview/checkpoints.
            time_column (str): Column name used for time-based filtering.
            start_time (str): Start time for filtering.
            end_time (str): End time for filtering.
            autoloader_location (str): Filesystem location for autoloader input.
            autoloader_format (str): Format of the data for autoloader.
            schema_file (str): Path to a file containing the schema definition.
            cloudfiles_schema_hints_file (str): Path to a file containing CloudFiles schema hints.
            cloudfiles_schema_hints (str): Directly provided CloudFiles schema hints.
            schema_uuid_str (str): Unique identifier for the schema (used in the autoloader schema path).
            schema (StructType): Schema definition for input data.
            data (dict): In-memory data used to create a DataFrame in "input" mode.
            pretransform_name (str): Name of the pre-transformation step.
            df (DataFrame): Internal Spark DataFrame loaded using the specified parameters.
        """
        self._spark = spark
        self._client = client  # Store client for lazy path resolution
        self._mode = None  # [input, table, autoloader, silverbronze]
        self._record_limit = 10
        self._autoloader_temp_schema_location = None  # Will be resolved lazily
        self._gold_test_schemas = []
        self._checkpoint_temp_location_base = None  # Will be resolved lazily

        self._time_column = None
        self._start_time = None
        self._end_time = None

        self._autoloader_location = None
        self._autoloader_format = None
        self._schema_file = None
        self._clouldfiles_schema_hints_file = None
        self._cloudfiles_schema_hints = None
        self._cloudfiles_reader_case_sensitive = "true"
        self._cloudfiles_multiline = "true"
        self._cloudfiles_wholetext = "false"
        self._schema_uuid_str = str(uuid.uuid4())
        self._single_variant_column = None

        self._schema = None
        self._data = None

        self._table = None

        self._bronze_tables = None

        self._pretransform_name = None

        self._df = None

    def _ensure_storage_paths_configured(self) -> None:
        """
        Ensure storage paths are configured, either from explicit user settings
        or from WorkspaceConfig. Only creates Client if paths are not explicitly set.

        Raises:
            RuntimeError: If daslStoragePath cannot be determined and paths not set
        """
        # If both paths already set explicitly, nothing to do
        if (
            self._autoloader_temp_schema_location is not None
            and self._checkpoint_temp_location_base is not None
        ):
            return

        # Need to get daslStoragePath from WorkspaceConfig
        if self._client is None:
            # Try to auto-create client
            try:
                from dasl_client import Client

                self._client = Client.for_workspace()
            except Exception as e:
                raise RuntimeError(
                    "Could not create DASL client to retrieve workspace configuration. "
                    "Either provide a client explicitly: PreviewParameters(spark, client=client), "
                    "or set storage paths manually:\n"
                    "  .set_autoloader_temp_schema_location('/path/to/schemas')\n"
                    "  .set_checkpoint_temp_location_base('/path/to/checkpoints')\n"
                    f"Client creation error: {e}"
                )

        # Get config and extract daslStoragePath
        try:
            config = self._client.get_config()
            dasl_storage_path = config.dasl_storage_path
        except Exception as e:
            raise RuntimeError(
                f"Failed to retrieve workspace configuration: {e}\n"
                "Set storage paths manually if WorkspaceConfig is not available:\n"
                "  .set_autoloader_temp_schema_location('/path/to/schemas')\n"
                "  .set_checkpoint_temp_location_base('/path/to/checkpoints')"
            )

        if not dasl_storage_path:
            raise RuntimeError(
                "WorkspaceConfig.dasl_storage_path is not set. "
                "Configure this in your workspace settings or set paths explicitly:\n"
                "  .set_autoloader_temp_schema_location('/path/to/schemas')\n"
                "  .set_checkpoint_temp_location_base('/path/to/checkpoints')"
            )

        # Build default paths from daslStoragePath
        if self._autoloader_temp_schema_location is None:
            self._autoloader_temp_schema_location = os.path.join(
                dasl_storage_path, "preset_preview", "schemas"
            )

        if self._checkpoint_temp_location_base is None:
            self._checkpoint_temp_location_base = os.path.join(
                dasl_storage_path, "preset_preview", "checkpoints"
            )

    def __create_from_autoloader(self) -> DataFrame:
        stream_df = (
            self._spark.readStream.format("cloudFiles")
            .option("cloudFiles.format", self._autoloader_format)
            .option("readerCaseSensitive", self._cloudfiles_reader_case_sensitive)
        )

        # text and wholetext needs to be handled seperately.
        stream_df = (
            stream_df.option("multiline", self._cloudfiles_multiline)
            if self._autoloader_format != "text"
            else stream_df.option("wholetext", self._cloudfiles_wholetext)
        )

        if self._single_variant_column:
            stream_df = stream_df.option(
                "singleVariantColumn", self._single_variant_column
            )

        if self._schema_file:
            with open(self._schema_file, "r") as f:
                stream_df = stream_df.schema(f.read().strip())
        else:
            stream_df = (
                stream_df.option("inferSchema", "true")
                .option("cloudFiles.inferColumnTypes", "true")
                .option(
                    "cloudFiles.schemaLocation",
                    os.path.join(
                        self.get_autoloader_temp_schema_location(),
                        self._schema_uuid_str,
                    ),
                )
            )

        if self._cloudfiles_schema_hints:
            stream_df = stream_df.option(
                "cloudFiles.schemaHints", self._cloudfiles_schema_hints
            )
        elif self._clouldfiles_schema_hints_file:
            stream_df = stream_df.option(
                "cloudFiles.schemaHintsFile", self._clouldfiles_schema_hints_file
            )

        stream_df = stream_df.load(self._autoloader_location).limit(self._record_limit)

        query = (
            stream_df.writeStream.format("memory")
            .queryName("batch_data")
            .trigger(availableNow=True)
            .option(
                "checkpointLocation",
                os.path.join(self.get_checkpoint_temp_location(), "memory"),
            )
            .start()
        )

        query.awaitTermination()

    def __create_from_silverbronze_tables_join(self) -> DataFrame:
        if not self._bronze_tables or not len(self._bronze_tables):
            raise MissingBronzeTablesError()

        # Validate name and joinExpr are set.
        for i in range(len(self._bronze_tables)):
            if not self._bronze_tables[i].get("name", None):
                raise MissingBronzeTableFieldError("name")
            if i > 0 and not self._bronze_tables[i].get("joinExpr", None):
                raise MissingBronzeTableFieldError("joinExpr")

        # If there is an autoloader location given, we create the df now and
        # then allow preBronze stage to run. Otherwise we skip preBronze stages
        # and as part of running the silverbronze joins we create the df from
        # the first entry in the bronze tables list.
        df = None
        if self._autoloader_location:
            self.__create_from_autoloader()
            df = self._spark.table("batch_data").alias(
                self._bronze_tables[0].get("name", "")
            )  # Use first's name.

        return df

    def __enter__(self):
        """
        Creates a DataFrame with data using the method specified. In the case of "autoloader",
        this will stream to a DataFrame that is then treated as a batch. This allows for easier
        emulation of some operations, while not giving up some of the options allowed by
        streaming.

        Returns:
            DataFrame: The resulting DataFrame with input data.
        """
        if self._mode == "input":
            self._df = self._spark.createDataFrame(self._data, self._schema)
        elif self._mode == "table":
            self._df = self._spark.table(self._table).limit(self._record_limit)
        elif self._mode == "autoloader":
            self.__create_from_autoloader()
            self._df = self._spark.table("batch_data")
        elif self._mode == "silverbronze":
            self._df = self.__create_from_silverbronze_tables_join()

        return self._df

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Cleans up the temporary schema created for streaming mode, if it was created.
        """
        # Only clean up if paths were actually configured
        # This handles the case where __exit__ is called after an exception in __enter__
        if (
            self._autoloader_temp_schema_location is None
            or self._checkpoint_temp_location_base is None
        ):
            return

        # Get the Databricks built-in functions out the namespace.
        ipython = get_ipython()
        if ipython is not None:
            dbutils = ipython.user_ns["dbutils"]

            dbutils.fs.rm(
                os.path.join(
                    self._autoloader_temp_schema_location, self._schema_uuid_str
                ),
                recurse=True,
            )
            dbutils.fs.rm(
                os.path.join(
                    self._checkpoint_temp_location_base, self._schema_uuid_str
                ),
                recurse=True,
            )
            for gold_test_schema in self._gold_test_schemas:
                dbutils.fs.rm(
                    os.path.join(
                        self._autoloader_temp_schema_location, gold_test_schema
                    ),
                    recurse=True,
                )
        else:
            leaked_lines = [
                f"FYI, we are leaking temp data {os.path.join(self._autoloader_temp_schema_location, self._schema_uuid_str)}",
                os.path.join(
                    self._checkpoint_temp_location_base, self._schema_uuid_str
                ),
                *[
                    os.path.join(self._autoloader_temp_schema_location, x)
                    for x in self._gold_test_schemas
                ],
            ]
            print(", ".join(leaked_lines))
        self._gold_test_schemas = []

    def from_input(self):
        """
        Set the data source loader to "input" mode. Requires a schema and data to be provided.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._mode = "input"
        return self

    def from_autoloader(self):
        """
        Set the data source loader to "autoloader" mode. Requires at least autoloader location
        to be provided.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._mode = "autoloader"
        return self

    def from_table(self):
        """
        Set the data source loader to "table" mode. Requires a table name to be provided.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._mode = "table"
        return self

    def from_silverbronze_tables(self):
        """
        Set the data source loader to "bronze tables" mode. Requires a list of bronze table
        definitions to be provided.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._mode = "silverbronze"
        return self

    def set_bronze_table_definitions(self, definitions: List[Dict[str, str]]):
        """
        Set the bronze table definitions for bronze tables mode. `name` and `joinExpr` are
        required. If `alias` is not provided, one can use the `name` to refer to the table.
        If `joinType` is not provided, "left" is used as a default value. If pr

        [
            {
                "name": "name",
                "alias": "alias1",
                "joinType": "inner",
                "joinExpr": "base_table.col1 = alias1.col1
            },
            ...
        ]
        """
        self._bronze_tables = definitions
        return self

    def set_autoloader_temp_schema_location(self, path: str):
        """
        Set the location for the autoloader's streaming mode schema to be created. This is
        deleted at the end of a run.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._autoloader_temp_schema_location = path
        return self

    def get_autoloader_temp_schema_location(self) -> str:
        """
        Get the location for the autoloader's streaming mode schema to be created.

        If not explicitly set, defaults to {daslStoragePath}/preset_preview/schemas.

        Returns:
             str: The location for the autoloader's streaming mode schema to be created.

        Raises:
            RuntimeError: If path cannot be determined from WorkspaceConfig
        """
        self._ensure_storage_paths_configured()
        return self._autoloader_temp_schema_location

    def set_checkpoint_temp_location_base(self, path: str):
        """
        Set the base location for the checkpoint to be created. This is
        deleted at the end of a run.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._checkpoint_temp_location_base = path
        return self

    def get_checkpoint_temp_location_base(self) -> str:
        """
        Get the location for the checkpoint to be created.

        If not explicitly set, defaults to {daslStoragePath}/preset_preview/checkpoints.

        Returns:
             str: The location for the checkpoint to be created.

        Raises:
            RuntimeError: If path cannot be determined from WorkspaceConfig
        """
        self._ensure_storage_paths_configured()
        return self._checkpoint_temp_location_base

    def get_checkpoint_temp_location(self) -> str:
        """
        Get the location where checkpoints to be created.

        Returns:
             str: The location where checkpoints to be created.

        Raises:
            RuntimeError: If path cannot be determined from WorkspaceConfig
        """
        self._ensure_storage_paths_configured()
        return os.path.join(self._checkpoint_temp_location_base, self._schema_uuid_str)

    def set_data_schema(self, schema: StructType):
        """
        Set the input schema for "input" mode. For example:

        StructType([
            StructField('name', StringType(), True),
            StructField('age', IntegerType(), True)
        ])

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._schema = schema
        return self

    def set_data(self, data: Dict[str, str]):
        """
        Set the input data for "input" mode. For example:

        [("Peter", 15), ("Urvi", 13), ("Graeme", 8)]

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._data = data
        return self

    def set_autoloader_location(self, location: str):
        """
        Set where to load data from for "autoloader" mode.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._autoloader_location = location
        return self

    def _set_autoloader_format(self, file_format: str):
        """
        Used internally to set the autoloader format.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        if file_format.lower() == "jsonl":
            self._autoloader_format = "json"
            self._cloudfiles_multiline = "false"
            return self
        if file_format.lower() == "wholetext":
            self._autoloader_format = "text"
            self._cloudfiles_wholetext = "true"
            return self
        self._autoloader_format = file_format
        return self

    def _set_autoloader_schema_file(self, path: str):
        """
        Set the schema file path for "autoloader" mode.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._schema_file = path
        return self

    def _set_autoloader_cloudfiles_schema_hint_file(self, path: str):
        """
        Set the cloudFiles schema hints file path for "autoloader" mode.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._clouldfiles_schema_hints_file = path
        return self

    def _set_autoloader_cloudfiles_schema_hints(self, cloudfiles_schema_hints: str):
        """
        Set the cloudFiles schema hints string for "autoloader" mode.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._cloudfiles_schema_hints = cloudfiles_schema_hints
        return self

    def set_pretransform_name(self, pretransform_name: str):
        """
        Set the pretransform name to use, if desired. If not set, Silver PreTransform
        will be skipped.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._pretransform_name = pretransform_name
        return self

    def set_date_range(self, column: str, start_time: str, end_time: str):
        """
        Set the TIMESTAMP column and date range to use as the input data filter to
        limit the number of records retrieved by the loader.

        Both start and end time must be TIMESTAMP compatible.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._time_column = column
        self._start_time = start_time
        self._end_time = end_time
        return self

    def set_input_record_limit(self, record_limit: int):
        """
        Set the LIMIT clause when retrieving records from the data source.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._record_limit = record_limit
        return self

    def set_table(self, table_name: str):
        """
        Set Unity Catalog table name for "table" mode.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._table = table_name
        return self

    def _set_load_as_single_variant(self, col_name: Optional[str] = None):
        """
        Enable loadAsSingleVariant mode. This will ingest data into a single VARIANT-typed column.
        The default name of that column is `data`.

        Returns:
            PreviewParameters: The current instance with updated configuration.
        """
        self._single_variant_column = col_name if col_name is not None else "data"
        return self

    def add_gold_schema_table(self, gold_schema_table_name: str):
        """
        Add a gold schema temporary table name that will need to be cleaned
        up at the end of the run.
        """
        self._gold_test_schemas.append(gold_schema_table_name)
