import base64
from typing import Optional

from dasl_api import ApiClient, Configuration, WorkspaceV1Api
from dasl_api.models import WorkspaceV1WorkspaceMetadata
from dasl_api.exceptions import ApiException

from .errors.errors import WorkspaceLookupError


class WorkspaceMetadata:
    """Workspace metadata lookup functionality for auto-detecting API endpoints."""

    @staticmethod
    def get_workspace_metadata(
        workspace_url: str, dasl_host: Optional[str] = None
    ) -> Optional[WorkspaceV1WorkspaceMetadata]:
        """
        Query the workspace metadata endpoint to auto-detect the correct region
        and API endpoint for a given Databricks workspace.

        :param workspace_url: The Databricks workspace URL to lookup
        :param dasl_host: Optional DASL host to use for the lookup. If None, uses default region.
        :returns: WorkspaceV1WorkspaceMetadata if successful, None if workspace not found
        """
        hosts = []
        if dasl_host is None:
            # Use default region for metadata lookup
            from .regions import Regions

            for region in Regions.list():
                hosts.append(Regions.lookup(region))
        else:
            hosts.append(dasl_host)

        last_exception = None
        for host in hosts:
            try:
                metadata = WorkspaceMetadata._get_workspace_metadata(
                    workspace_url, host
                )
                if metadata:
                    return metadata
            except WorkspaceLookupError as e:
                last_exception = e
                continue

        if last_exception:
            raise last_exception
        return None

    @staticmethod
    def _get_workspace_metadata(
        workspace_url: str, dasl_host: str
    ) -> Optional[WorkspaceV1WorkspaceMetadata]:
        try:
            # Create an unauthenticated client for the public metadata endpoint
            configuration = Configuration(host=dasl_host)
            api_client = ApiClient(configuration)
            workspace_api = WorkspaceV1Api(api_client)

            # Base64 encode the workspace URL
            encoded_workspace = base64.urlsafe_b64encode(
                workspace_url.encode()
            ).decode()

            # Call the metadata endpoint
            metadata = workspace_api.workspace_v1_get_workspace_metadata(
                databricks_workspace=encoded_workspace
            )

            return metadata

        except ApiException as e:
            if e.status == 404:
                # Workspace not found or not in supported region
                return None
            elif e.status == 400:
                # Invalid workspace URL
                raise ValueError(f"Invalid workspace URL: {workspace_url}")
            else:
                # Other API errors
                raise WorkspaceLookupError(f"Failed to get workspace metadata: {e}")
        except Exception as e:
            # Network errors, encoding errors, etc.
            raise WorkspaceLookupError(f"Failed to get workspace metadata: {e}")

    @staticmethod
    def get_endpoint_for_workspace(workspace_url: str) -> Optional[str]:
        """
        Get the API endpoint URL for a workspace.

        :param workspace_url: The Databricks workspace URL
        :returns: API endpoint URL if successful, None if workspace not found
        """
        metadata = WorkspaceMetadata.get_workspace_metadata(workspace_url)
        if metadata is not None:
            return metadata.api_url
        return None
