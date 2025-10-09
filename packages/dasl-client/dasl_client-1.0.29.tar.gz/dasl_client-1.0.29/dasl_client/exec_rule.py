from pyspark.sql import DataFrame
from typing import List, Optional

from dasl_api import CoreV1RenderedRuleTables


class ExecRule:
    """
    ExecRule result object allowing access to and clean up of tables
    created as part of the rule rendering endpoint. While the table
    names are exposed as attributes, there are helper functions for
    fetching the contents of the most common tables (i.e. notables
    and observables). In general, it won't be necessary to access
    these attributes. Note that you must call the cleanup function
    when you are done with an instance of this class or else tables
    created as part of rendering and running the rule will be left
    orphaned in your workspace.

    Attributes:
        notables_table (str):
            name of table where notables for the rule execution
            can be found.
        observables_table (str):
            name of table where observables for the rule execution
            can be found.
        opals_table (str):
            name of table where operational alerts for the rule execution
            can be found.
        data_metrics_table (str):
            name of table where rule metrics for the rule execution
            can be found.
        stream_metrics_table (str):
            name of table where stream metrics for the rule execution
            can be found.
        observables_acc_table (str):
            name of table where observables aggregation for the rule
            execution can be found.
    """

    def __init__(self, spark, tables: CoreV1RenderedRuleTables):
        self.spark = spark
        self.notables_table = tables.notables
        self.observables_table = tables.observables
        self.opals_table = tables.operational_alerts
        self.data_metrics_table = tables.data_metrics
        self.stream_metrics_table = tables.stream_metrics
        self.observables_acc_table = tables.observables_accumulation

    def _all_tables(self) -> List[str]:
        return [
            self.notables_table,
            self.observables_table,
            self.opals_table,
            self.data_metrics_table,
            self.stream_metrics_table,
            self.observables_acc_table,
        ]

    def cleanup(self):
        """
        Clean up when done with this ExecRule instance. This method
        cleans up temporarily allocated tables used to store the
        results of the rule execution. Unless you need to preserve
        the results for some reason, you must call this method or
        the temporary tables will be orphaned in your workspace.
        """
        for table in self._all_tables():
            self.spark.sql(f"DROP TABLE IF EXISTS {table}")

    def notables(self, limit: Optional[int] = None) -> DataFrame:
        """
        Return the contents of the notables table.

        :param limit: optional limit to the number of rows returned.
        :returns: DataFrame containing the notables table rows.
        """
        query = f"SELECT * FROM {self.notables_table}"
        if limit is not None:
            query = f"{query} LIMIT {limit}"
        return self.spark.sql(query)

    def observables(self, limit: Optional[int] = None) -> DataFrame:
        """
        Return the contents of the observables table.

        :param limit: optional limit to the number of rows returned.
        :returns: DataFrame containing the observables table rows.
        """
        query = f"SELECT * FROM {self.observables_table}"
        if limit is not None:
            query = f"{query} LIMIT {limit}"
        return self.spark.sql(query)
