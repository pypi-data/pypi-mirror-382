from copy import deepcopy
from datetime import datetime, timedelta
from time import sleep
from typing import Any, Callable, Iterator, List, Optional, TypeVar

from dasl_api import (
    ContentV1Api,
    CoreV1Api,
    CoreV1QueryExtendRequestDateRange,
    DbuiV1Api,
    DbuiV1QueryExtendRequest,
    DbuiV1QueryGenerateRequest,
    DbuiV1QueryGenerateRequestTimeRange,
    DbuiV1QueryGenerateStatus,
    DbuiV1QueryHistogramRequest,
    DbuiV1QueryHistogramResult,
    DbuiV1QueryLookupRequest,
    DbuiV1QueryLookupRequestPagination,
    DbuiV1QueryLookupResult,
    WorkspaceV1Api,
    WorkspaceV1CreateWorkspaceRequest,
    api,
)
from dasl_client.auth.auth import (
    Authorization,
    DatabricksSecretAuth,
    ServiceAccountKeyAuth,
)
from dasl_client.conn.conn import get_base_conn
from dasl_client.errors.errors import ConflictError, error_handler
from dasl_client.metadata import WorkspaceMetadata

from .exec_rule import ExecRule
from .helpers import Helpers
from .regions import Regions
from .types import (
    AdminConfig,
    DataSource,
    DataSourcePreset,
    DataSourcePresetsList,
    Dbui,
    Metadata,
    Rule,
    TransformRequest,
    TransformResponse,
    WorkspaceConfig,
)

T = TypeVar("T")


class Client:
    """
    Antimatter security lakehouse client.
    """

    def __init__(
        self,
        auth: Authorization,
    ):
        """
        Initialize a new client. You should generally prefer to use
        the new_workspace function if creating a new workspace or the
        for_workspace function if connecting to an existing workspace.

        :param auth: Authorization instance for authorizing requests to
            the dasl control plane.
        :returns: Client
        """
        self.auth = auth

    @staticmethod
    def new_workspace(
        admin_email: str,
        app_client_id: str,
        service_principal_id: str,
        service_principal_secret: str,
        workspace_url: Optional[str] = None,
        region: Optional[str] = None,
        dasl_host: Optional[str] = None,
    ) -> "Client":
        """
        Register a new workspace and return a client for it.

        :param admin_email: The email address associated with the (DASL)
            workspace admin, if the workspace will be created.
        :param app_client_id: The Databricks app connection client ID
            to use for authentication calls related to the workspace.
        :param service_principal_id: The ID of the Databricks service
            principal that will interact with Databricks on your behalf.
        :param service_principal_secret: An OAuth secret that entitles
            the service principal to make Databricks API calls on your
            behalf.
        :param workspace_url: The full base URL of the Databricks workspace
            being registered. If you omit this value, it will be inferred
            if you are running within a Databricks notebook. Otherwise, an
            exception will be raised.
        :param region: The name of the DASL region. If not specified,
            the client will auto-detect the region from the workspace
            URL. For a DASL region, this includes the cloud host, e.g.
            aws-us-east-1.
        :param dasl_host: The URL of the DASL server. This value should
            not generally be specified. When specified, this value
            overrides both region and auto-detection.
        :returns: Client for the newly created workspace.
        """
        with error_handler():
            if workspace_url is None:
                workspace_url = Helpers.current_workspace_url()

            # Determine the DASL host to use
            dasl_host = Client._dasl_host_from_workspace_metadata(
                workspace_url, dasl_host, region
            )

            admin_config = AdminConfig(
                workspace_url=workspace_url,
                app_client_id=app_client_id,
                service_principal_id=service_principal_id,
                service_principal_secret=service_principal_secret,
            )
            workspace_name = Helpers.workspace_name_from_url(workspace_url)
            api_key = (
                api.WorkspaceV1Api(api_client=get_base_conn(host=dasl_host))
                .workspace_v1_create_workspace(
                    WorkspaceV1CreateWorkspaceRequest(
                        admin_user=admin_email,
                        workspace_name=workspace_name,
                        admin_config=admin_config.to_api_obj().spec,
                    )
                )
                .admin_service_account.apikey
            )
            return Client(
                ServiceAccountKeyAuth(workspace_name, api_key, host=dasl_host),
            )

    # TODO: should we allow user to use an API key here?
    @staticmethod
    def for_workspace(
        workspace_url: Optional[str] = None,
        service_account_token: Optional[str] = None,
        region: Optional[str] = None,
        dasl_host: Optional[str] = None,
    ) -> "Client":
        """
        Create a client for the argument workspace, if specified, or
        the current workspace if running in databricks notebook context.

        :param workspace_url: The full base URL of the Databricks workspace
            being registered. If you omit this value, it will be inferred
            if you are running within a Databricks notebook. Otherwise,
            an exception will be raised.
        :param service_account_token: Antimatter service account token.
            If provided, the client will use this token for auth instead
            of (automatic) secret-based auth.
        :param region: The name of the DASL region. If not specified,
            the client will auto-detect the region from the workspace
            URL. For a DASL region, this includes the cloud host, e.g.
            aws-us-east-1.
        :param dasl_host: The URL of the DASL server. This value should
            not generally be specified. When specified, this value
            overrides both region and auto-detection.
        :returns: Client for the existing workspace.
        """
        with error_handler():
            if workspace_url is None:
                workspace_url = Helpers.current_workspace_url()

            # Determine the DASL host to use
            dasl_host = Client._dasl_host_from_workspace_metadata(
                workspace_url, dasl_host, region
            )

            if service_account_token is None:
                return Client(
                    DatabricksSecretAuth(
                        Helpers.workspace_name_from_url(workspace_url),
                        host=dasl_host,
                    ),
                )
            else:
                return Client(
                    ServiceAccountKeyAuth(
                        Helpers.workspace_name_from_url(workspace_url),
                        service_account_token,
                        host=dasl_host,
                    )
                )

    @staticmethod
    def new_or_existing(
        admin_email: str,
        app_client_id: str,
        service_principal_id: str,
        service_principal_secret: str,
        workspace_url: Optional[str] = None,
        service_account_token: Optional[str] = None,
        region: Optional[str] = None,
        dasl_host: Optional[str] = None,
    ) -> "Client":
        """
        Initialize a new client for the workspace associated with the
        argument Databricks workspace_url. If no such workspace exists,
        one will be created for you.

        :param admin_email: The email address associated with the (DASL)
            workspace admin, if the workspace will be created. Ignored if
            the workspace already exists.
        :param app_client_id: The Databricks app connection client ID
            to use for authentication calls related to the workspace. If
            the workspace already exists, the existing config will be
            updated to use this client ID.
        :param service_principal_id: The ID of the Databricks service
            principal that will interact with Databricks on your behalf.
            If the workspace already exists, the existing config will be
            updated to use this service principal ID.
        :param service_principal_secret: An OAuth secret that entitles
            the service principal to make Databricks API calls on your
            behalf. If the workspace already exists, the existing config
            will be updated to use this service principal secret.
        :param workspace_url: The full base URL of the Databricks workspace
            being registered. If you omit this value, it will be inferred
            if you are running within a Databricks notebook. Otherwise, an
            exception will be raised. If the workspace already exists, the
            existing config will be updated to use this value.
        :param service_account_token: Antimatter service account token.
            If provided, the client will use this token for auth instead
            of (automatic) secret-based auth. Ignored if the workspace
            doesn't exist.
        :param region: The name of the DASL region. If not specified,
            the client will auto-detect the region from the workspace
            URL. For a DASL region, this includes the cloud host, e.g.
            aws-us-east-1.
        :param dasl_host: The URL of the DASL server. This value should
            not generally be specified. When specified, this value
            overrides both region and auto-detection.
        :returns: Client for the newly created or existing workspace.
        """
        try:
            return Client.new_workspace(
                admin_email,
                app_client_id,
                service_principal_id,
                service_principal_secret,
                workspace_url,
                region,
                dasl_host,
            )
        except ConflictError:
            result = Client.for_workspace(
                workspace_url, service_account_token, region, dasl_host
            )
            result.put_admin_config(
                AdminConfig(
                    workspace_url=workspace_url,
                    app_client_id=app_client_id,
                    service_principal_id=service_principal_id,
                    service_principal_secret=service_principal_secret,
                )
            )
            return result

    def _workspace_client(self) -> WorkspaceV1Api:
        return WorkspaceV1Api(self.auth.client())

    def _core_client(self) -> CoreV1Api:
        return CoreV1Api(self.auth.client())

    def _dbui_client(self) -> DbuiV1Api:
        return DbuiV1Api(self.auth.client())

    def _content_client(self) -> ContentV1Api:
        return ContentV1Api(self.auth.client())

    def _workspace(self) -> str:
        return self.auth.workspace()

    def _list_iter_paginated(
        self,
        list_func: Callable[..., Any],
        convert: Callable[[Any], T],
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Iterator[T]:
        """
        Generic helper for paginated list functions.
        """
        current_cursor = cursor
        results_so_far = 0
        while True:
            page_limit = limit - results_so_far if limit is not None else None
            if limit is not None and page_limit <= 0:
                break

            with error_handler():
                response = list_func(
                    workspace=self._workspace(),
                    cursor=current_cursor,
                    limit=page_limit,
                )

            for item in response.items:
                yield convert(item)
                results_so_far += 1

            current_cursor = (
                response.metadata.cursor if hasattr(response, "metadata") else None
            )
            if current_cursor is None:
                break

    def get_admin_config(self) -> AdminConfig:
        """
        Retrieve the AdminConfig from the DASL server. Note that the
        service principal secret will be redacted server side, so if you
        plan to make changes and issue a request using put_admin_config,
        you will need to repopulate the service_principal_secret correctly
        before passing the result back to put_admin_config.

        :returns: AdminConfig containing the current settings.
        """
        with error_handler():
            return AdminConfig.from_api_obj(
                self._workspace_client().workspace_v1_get_admin_config(
                    self._workspace()
                )
            )

    def put_admin_config(
        self,
        config: AdminConfig,
    ) -> None:
        """
        Update the AdminConfig stored in the DASL server. See the AdminConfig
        docs for details about its contents.

        :param config: AdminConfig to replace the existing. Note that the
            service principal credentials will be verified server side before
            the request is accepted.
        """
        with error_handler():
            self._workspace_client().workspace_v1_put_admin_config(
                self._workspace(),
                config.to_api_obj(),
            )

    def get_config(self) -> WorkspaceConfig:
        """
        Retrieve the WorkspaceConfig from the DASL server. The returned
        value can be updated directly and passed to put_config in order
        to make changes.

        :returns: WorkspaceConfig containing the current configuration.
        """
        with error_handler():
            return WorkspaceConfig.from_api_obj(
                self._workspace_client().workspace_v1_get_config(self._workspace())
            )

    def put_config(
        self,
        config_in: WorkspaceConfig,
    ) -> None:
        """
        Update the WorkspaceConfig stored in the DASL server. See the
        WorkspaceConfig docs for dtails about its contents.

        :param config_in: WorkspaceConfig to replace the existing.
        :returns: WorkspaceConfig. Note that the returned value is a
            clone of config_in and may not be precisely equal to the
            originally passed value.
        """
        with error_handler():
            config = deepcopy(config_in)
            if config.metadata is None:
                config.metadata = Metadata(
                    name="config",
                    workspace=self._workspace(),
                )

            # reset the version; let the server set the version for us
            config.metadata.version = None

            self._workspace_client().workspace_v1_put_config(
                self._workspace(),
                config.to_api_obj(),
            )

    def get_datasource(self, name: str) -> DataSource:
        """
        Get the DataSource with the argument name from the DASL server. The
        returned value can be updated directly and passed to update_datasource
        in order to make changes.

        :param name: The unique name of the DataSource within this workspace
        :returns: DataSource
        """
        with error_handler():
            return DataSource.from_api_obj(
                self._core_client().core_v1_get_data_source(self._workspace(), name)
            )

    def delete_datasource(self, name: str) -> None:
        """
        Delete the DataSource with the argument name from the DASL server.
        The DataSource will not necessarily be deleted immediately as the
        server will dispatch background tasks to clean up any allocated
        resources before actually deleting the resource, so it may take
        some time before its name is available for reuse.

        :param name: The unique name of the DataSource within this workspace
        """
        with error_handler():
            self._core_client().core_v1_delete_data_source(self._workspace(), name)

    def list_datasources(
        self, cursor: Optional[str] = None, limit: Optional[int] = None
    ) -> Iterator[DataSource]:
        """
        List the DataSources in this workspace. Each yielded DataSource
        contains all fields in the DataSource as if it were fetched
        using the get_datasource method.

        :param cursor: The ID of a DataSource. If specified, the results
            will contain DataSources starting (lexically) directly after
            this DataSource. If not specified, then the results will begin
            with the lexically least DataSource.
        :param limit: The maximum number of DataSources to yield. If there
            are fewer than this number of DataSources beginning directly
            after `cursor`, then all such DataSources will be yielded. If
            not specified, then all DataSources starting directly after
            `cursor` will be returned.
        :yields DataSource: One DataSource at a time in lexically
            increasing order
        """
        return self._list_iter_paginated(
            list_func=self._core_client().core_v1_list_data_sources,
            convert=DataSource.from_api_obj,
            cursor=cursor,
            limit=limit,
        )

    def create_datasource(self, name: str, ds_in: DataSource) -> DataSource:
        """
        Create a new DataSource. The chosen name must be unique for your
        workspace, and cannot refer to a DataSource that already exists
        and has not been deleted. See the documentation for delete_datasource
        as there are some caveats around name reuse.

        :param name: The unique name of this DataSource in the workspace.
        :param ds_in: The specification of the DataSource to create. See
            the documentation for the DataSource type for more details.
        :returns DataSource: Note that the returned value is a
            clone of ds_in and may not be precisely equal to the
            originally passed value.
        """
        with error_handler():
            ds = deepcopy(ds_in)
            if ds.metadata is None:
                ds.metadata = Metadata(
                    name=name,
                    workspace=self._workspace(),
                )

            result = self._core_client().core_v1_create_data_source(
                self._workspace(), ds.to_api_obj()
            )
            return DataSource.from_api_obj(result)

    def replace_datasource(self, name: str, ds_in: DataSource) -> DataSource:
        """
        Replace an existing DataSource. The name must refer to a DataSource
        that already exists in your workspace.

        :param name: The name of the existing DataSource to replace.
        :param ds_in: The specification of the DataSource taking the place
            of the existing DataSource.
        :returns DataSource: Note that the returned value is a
            clone of ds_in and may not be precisely equal to the
            originally passed value.
        """
        with error_handler():
            ds = deepcopy(ds_in)
            if ds.metadata is None:
                ds.metadata = Metadata(
                    name=name,
                    workspace=self._workspace(),
                )

            # reset the version; let the server set the version for us
            ds.metadata.version = None

            result = self._core_client().core_v1_replace_data_source(
                self._workspace(),
                name,
                ds.to_api_obj(),
            )
            return DataSource.from_api_obj(result)

    def get_rule(self, name: str) -> Rule:
        """
        Get the Rule with the argument name from the DASL server. The
        returned value can be updated directly and passed to update_rule
        in order to make changes.

        :param name: The unique name of the Rule within this workspace
        :returns: Rule
        """
        with error_handler():
            return Rule.from_api_obj(
                self._core_client().core_v1_get_rule(self._workspace(), name)
            )

    def delete_rule(self, name: str) -> None:
        """
        Delete the Rule with the argument name from the DASL server.
        The Rule will not necessarily be deleted immediately as the
        server will dispatch background tasks to clean up any allocated
        resources before actually deleting the resource, so it may take
        some time before its name is available for reuse.

        :param name: The unique name of the Rule within this workspace
        """
        with error_handler():
            self._core_client().core_v1_delete_rule(self._workspace(), name)

    def list_rules(
        self, cursor: Optional[str] = None, limit: Optional[int] = None
    ) -> Iterator[Rule]:
        """
        List the Rules in this workspace. Each yielded Rule contains
        all fields in the Rule as if it were fetched using the
        get_rule method.

        :param cursor: The ID of a Rule. If specified, the results will
            contain DataSources starting (lexically) directly after this
            Rule. If not specified, then the results will begin with the
            lexically least Rule.
        :param limit: The maximum number of Rules to yield. If there are
            fewer than this number of Rules beginning directly after
            `cursor`, then all such Rules will be yielded. If not specified,
            then all Rules starting directly after `cursor` will be returned.
        :yields Rule: One Rule at a time in lexically increasing order.
        """
        return self._list_iter_paginated(
            list_func=self._core_client().core_v1_list_rules,
            convert=Rule.from_api_obj,
            cursor=cursor,
            limit=limit,
        )

    def create_rule(self, name: str, rule_in: Rule) -> Rule:
        """
        Create a new Rule. The chosen name must be unique for your
        workspace, and cannot refer to a Rule that already exists
        and has not been deleted. See the documentation for delete_rule
        as there are some caveats around name reuse.

        :param name: The unique name of this Rule in the workspace.
        :param rule_in: The specification of the Rule to create. See
            the documentation for the Rule type for more details.
        :returns Rule: Note that the returned value is a clone of
            rule_in and may not be precisely equal to the originally
            passed value.
        """
        with error_handler():
            rule = deepcopy(rule_in)
            if rule.metadata is None:
                rule.metadata = Metadata(
                    name=name,
                    workspace=self._workspace(),
                )

            result = self._core_client().core_v1_create_rule(
                self._workspace(), rule.to_api_obj()
            )
            return Rule.from_api_obj(result)

    def replace_rule(self, name: str, rule_in: Rule) -> Rule:
        """
        Replace an existing Rule. The name must refer to a Rule
        that already exists in your workspace.

        :param name: The name of the existing Rule to replace.
        :param rule_in: The specification of the Rule taking the place
            of the existing Rule.
        :returns Rule: Note that the returned value is a clone of
            rule_in and may not be precisely equal to the originally
            passed value.
        """
        with error_handler():
            rule = deepcopy(rule_in)
            if rule.metadata is None:
                rule.metadata = Metadata(
                    name=name,
                    workspace=self._workspace(),
                )

            # reset the version; let the server set the version for us
            rule.metadata.version = None

            result = self._core_client().core_v1_replace_rule(
                self._workspace(),
                name,
                rule.to_api_obj(),
            )
        return Rule.from_api_obj(result)

    def exec_rule(
        self,
        spark,
        rule_in: Rule | str,
    ) -> ExecRule:
        """
        Locally execute a Rule. Must be run from within a Databricks
        notebook or else an exception will be raised. This is intended
        to facilitate Rule development.

        :param spark: Spark context from Databricks notebook. Will be
            injected into the execution environment for use by the
            Rule notebook.
        :param rule_in:
            The specification of the Rule to execute. If specified as
            a string, it should be in YAML format.
        :returns ExecRule: A class containing various information and
            functionality relating to the execution. See the docs for
            ExecRule for additional details, but note that you must
            call its cleanup function or tables created just for this
            request will leak.
        """
        rule = rule_in
        if isinstance(rule_in, str):
            rule = Rule.from_yaml_str(rule_in)

        Helpers.ensure_databricks()

        with error_handler():
            result = self._core_client().core_v1_render_rule(
                self._workspace(),
                rule.to_api_obj(),
            )

            try:
                import notebook_utils
            except ImportError as e:
                raise ImportError(
                    "Package 'notebook_utils' not found. "
                    "Install it within this this notebook using "
                    f"%pip install {result.notebook_utils_path}"
                )

            exec(result.content, {"spark": spark})
            return ExecRule(spark, result.tables)

    def adhoc_transform(
        self,
        warehouse: str,
        request: TransformRequest,
        timeout: timedelta = timedelta(minutes=5),
    ) -> TransformResponse:
        """
        Run a sequence of ADHOC transforms against a SQL warehouse to
        mimic the operations performed by a datasource.

        :param warehouse: The warehouse ID to run the transforms against.
        :param request: The request containing the transforms to run.
        :return: a TransformResponse object containing the results
            after running the transforms.
        :raises: NotFoundError if the rule does not exist
        :raises: Exception for a server-side error or timeout
        """
        with error_handler():
            status = self._dbui_client().dbui_v1_transform(
                self._workspace(),
                warehouse,
                request.to_api_obj(),
            )

            begin = datetime.now()
            while datetime.now() - begin < timeout:
                sleep(5)
                status = self._dbui_client().dbui_v1_transform_status(
                    self._workspace(), status.id
                )

                if status.status == "failed":
                    raise Exception(f"adhoc transform failed with {status.error}")
                elif status.status == "succeeded":
                    return TransformResponse.from_api_obj(status.result)

            raise Exception("timed out waiting for adhoc transform result")

    def get_observable_events(
        self,
        warehouse: str,
        kind: str,
        value: str,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dbui.ObservableEvents.EventsList:
        """
        Get the observable events associated with a specific field and value.

        :param warehouse: The warehouse id to perform the operation on
        :param kind: The observable kind
        :param value: The observable value
        :param cursor: A cursor to be used when paginating results
        :param limit: A limit of the number of results to return
        :returns: EventsList
        """
        with error_handler():
            return Dbui.ObservableEvents.EventsList.from_api_obj(
                self._dbui_client().dbui_v1_get_observable_events(
                    self._workspace(),
                    warehouse=warehouse,
                    kind=kind,
                    value=value,
                    cursor=cursor,
                    limit=limit,
                )
            )

    def list_presets(self) -> DataSourcePresetsList:
        """
        List the Presets in this workspace. This will include any user defined
        presets if a custom presets path has been configured in the workspace.

        :returns: DataSourcePresetsList
        """
        with error_handler():
            return DataSourcePresetsList.from_api_obj(
                self._content_client().content_v1_get_preset_data_sources(
                    self._workspace(),
                )
            )

    def get_preset(self, name: str) -> DataSourcePreset:
        """
        Get the preset with the argument name from the DASL server. If the preset name
        begins with 'internal_' it will instead be collected from the user catalog,
        provided a preset path is set in the workspace config.

        :param name: The unique name of the DataSource preset within this workspace.
        :returns: DataSourcePreset
        """
        with error_handler():
            return DataSourcePreset.from_api_obj(
                self._content_client().content_v1_get_preset_datasource(
                    self._workspace(), name
                )
            )

    def purge_preset_cache(self) -> None:
        """
        Purge the datasource cache presets. This will cause the DASL workspace
        to fetch presets from provided sources.
        """
        with error_handler():
            self._content_client().content_v1_preset_purge_cache(self._workspace())

    def generate_query(
        self,
        sql: str,
        warehouse: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> str:
        """
        Generate a query from the given SQL.

        :param sql: The SQL to use to create the query data set.
        :param warehouse: The SQL warehouse use to execute the SQL. If
            omitted, the default SQL warehouse specified in the workspace
            config will be used.
        :param start_date: The optional starting date to filter by for
            the provided sql used to create the data set. Only rows with
            their time column (see the time_col parameter) greater than
            or equal to this value will be included in the data set. You
            must specify a value for this parameter if you wish to filter
            by time. Valid values include actual timestamps and computed
            timestamps (such as now()).
        :param end_date: The optional ending date to filter by for the
            provided sql used to create the data set. The same caveats
            apply as with the start_time parameter. However, this parameter
            is not required and if omitted when a start_date is provided,
            the current date will be used.
        :returns str: The ID of the query generation operation. This value
            can be used with get_query_status to track the progress of
            the generation process, and eventually to perform lookups
            on the completed query.
        """
        time_range = None
        if start_date is not None or end_date is not None:
            time_range = DbuiV1QueryGenerateRequestTimeRange(
                startDate=start_date,
                endDate=end_date,
            )

        req = DbuiV1QueryGenerateRequest(
            warehouse=warehouse,
            sql=sql,
            timeRange=time_range,
        )

        with error_handler():
            return (
                self._dbui_client()
                .dbui_v1_query_generate(
                    self._workspace(),
                    req,
                )
                .id
            )

    def extend_query(
        self,
        id: str,
        warehouse: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> str:
        """
        Extend an existing query to cover a larger time range . If the query
        is ordered by time and contains no aggregations, this will add the
        additional data to the existing underlying query, returning the
        existing ID. If the existing table cannot be extended, a new table
        will be created to cover the updated time range.

        :param id: The ID of the query to extend.
        :param warehouse: The SQL warehouse use to execute the SQL. If
            omitted, the default SQL warehouse specified in the workspace
            config will be used.
        :param start_date: An optional starting date to extend the existing
            query by. If not provided, the current start date of the query
            will be used.
        :param end_date: An optional end date to extend the existing
            query by. If not provided, the current end date of the query
            will be used.
        :returns str: The ID of the query generation operation. This value
            can be used with get_query_status to track the progress of
            the generation process, and eventually to perform lookups
            on the completed query. If the current query could be extended,
            this id will be the same as the one provided. If a new query had
            to be generated, the new ID is returned.
        """
        time_range = None
        if start_date is not None or end_date is not None:
            time_range = CoreV1QueryExtendRequestDateRange(
                startDate=start_date,
                endDate=end_date,
            )

        req = DbuiV1QueryExtendRequest(
            warehouse=warehouse,
            timeRange=time_range,
        )

        with error_handler():
            return (
                self._dbui_client()
                .dbui_v1_query_extend(
                    self._workspace(),
                    id,
                    req,
                )
                .id
            )

    def get_query_status(
        self,
        id: str,
    ) -> DbuiV1QueryGenerateStatus:
        """
        Check the status of a query generation operation. Since generation
        happens in the background, it is up to the caller to check the
        status until the return value's status member is either equal to
        "succeeded" or "failed".

        :param id: The id of the query generation operation.
        :returns DbuiV1QueryGenerateStatus: The imporant field is
            status (as used in the example code).

        The following example demonstrates usage of the API.

        Example:
        id = client.generate_query("SELECT now() as time")
        result = None
        while True:
            time.sleep(3)
            status = client.get_query_status(id)
            if status.status == "failed":
                raise Exception("query failed")
            if status.status == "succeeded":
                break
        """
        with error_handler():
            return self._dbui_client().dbui_v1_query_generate_status(
                self._workspace(),
                id,
            )

    def query_lookup(
        self,
        id: str,
        warehouse: Optional[str] = None,
        pagination: Optional[DbuiV1QueryLookupRequestPagination] = None,
        start_value: Optional[str] = None,
        row_count: Optional[int] = None,
        refinements: Optional[List[str]] = None,
    ) -> DbuiV1QueryLookupResult:
        """
        Perform a lookup on a query, which applies refinements to the
        query and returns the results.

        :param id: The query ID returned from query_generate and
            get_query_status.
        :param warehouse: The optional SQL warehouse ID to use to compute
            the results. If not specified, uses the default SQL warehouse
            configured for the workspace.
        :param pagination: A sequence of fields and a direction that can
            be applied to a lookup request. If 'fetchPreceding' is true,
            the prior n rows up to the first row that matches the provided
            fields will be returned. Otherwise, the n rows following the
            first row that matches the provided fields will be returned.
        :param start_value: An optional start value to constrain the data
            being returned. This will  be applied to the primary ordering
            column if provided, before any refinements.
        :param row_count: The maximum number of rows to include in a page.
            Defaults to 1000, and must be in the range [1,1000].
        :param refinements: Pipeline filters to be applied to the result.
            Any SQL which is valid as a pipeline stage (i.e. coming between
            |> symbols) is valid here, such as ORDER BY id, or WHERE
            column = 'value'.
        """
        with error_handler():
            return self._dbui_client().dbui_v1_query_lookup(
                self._workspace(),
                id,
                DbuiV1QueryLookupRequest(
                    warehouse=warehouse,
                    startValue=start_value,
                    pagination=pagination,
                    rowCount=row_count,
                    refinements=refinements,
                ),
            )

    def query_histogram(
        self,
        id: str,
        interval: str,
        warehouse: Optional[str] = None,
        start_date: str = None,
        end_date: Optional[str] = None,
        refinements: Optional[List[str]] = None,
    ) -> DbuiV1QueryHistogramResult:
        """
        Perform a lookup on a query, which applies refinements to the
        query and returns the results.

        :param id: The query ID returned from query_generate and
            get_query_status.
        :param warehouse: The optional SQL warehouse ID to use to compute
            the results. If not specified, uses the default SQL warehouse
            configured for the workspace.
        :param start_date: The start date filter. The resulting frequency
            map will be restricted to rows where the time column value
            is greater than or equal to this value. Valid values include
            literal timestamps and function calls such as now().
        :param end_date: The optional end date filter. If specified, the
            resulting frequency map will contain only rows where the time
            column value is less than or equal to this value.
        :param interval: The duration of each interval in the resulting
            frequency map. This must be an interval string in  the format:
            '1 day', '3 minutes 2 seconds', '2 weeks'.
        :param refinements: Pipeline filters to be applied to the result.
            Any SQL which is valid as a pipeline stage (i.e. coming between
            |> symbols) is valid here, such as ORDER BY id, or WHERE
            column = 'value'.
        """
        with error_handler():
            return self._dbui_client().dbui_v1_query_histogram(
                self._workspace(),
                id,
                DbuiV1QueryHistogramRequest(
                    warehouse=warehouse,
                    startDate=start_date,
                    endDate=end_date,
                    interval=interval,
                    refinements=refinements,
                ),
            )

    def query_cancel(self, id: str) -> None:
        """
        Cancel an existing query.

        :param id: The query ID returned from query_generate and
            get_query_status.
        """
        with error_handler():
            return self._dbui_client().dbui_v1_query_cancel(self._workspace(), id)

    @staticmethod
    def _dasl_host_from_workspace_metadata(
        workspace_url: str, dasl_host: Optional[str], region: Optional[str]
    ) -> str:
        """
        If the dasl_host is already set, it will be returned as-is. If a region
        is set, this will return the host that region maps to. If neither are
        set, this gets the DASL host from the workspace URL with a workspace
        metadata lookup.

        :param workspace_url: The full base URL of the Databricks workspace
            being registered. If you omit this value, it will be inferred
            if you are running within a Databricks notebook. Otherwise, an
            exception will be raised.
        :param dasl_host: The URL of the DASL server. This value should
            not generally be specified. When specified, this value
            overrides both region and auto-detection.
        :param region: The name of the DASL region. If not specified,
            the client will auto-detect the region from the workspace
            URL. For a DASL region, this includes the cloud host, e.g.
            aws-us-east-1.
        :return: The DASL host to use.
        """
        if dasl_host is None:
            if region is not None:
                # Use explicit region
                dasl_host = Regions.lookup(region)
            else:
                # Attempt auto-detection from workspace URL
                try:
                    metadata = WorkspaceMetadata.get_workspace_metadata(workspace_url)
                    if metadata is not None:
                        dasl_host = metadata.api_url
                    else:
                        raise Exception(
                            f"Could not determine API endpoint for workspace '{workspace_url}'. "
                            f"The workspace may not be in a supported region. "
                            f"Please specify 'region' or 'dasl_host' explicitly."
                        )
                except Exception as e:
                    if "Could not determine API endpoint" in str(e):
                        raise
                    else:
                        raise Exception(
                            f"Failed to auto-detect API endpoint for workspace '{workspace_url}': {e}. "
                            f"Please specify 'region' or 'dasl_host' explicitly."
                        )
        return dasl_host
