from typing import Optional

from automizor import session
from automizor.exceptions import AutomizorError
from automizor.utils import get_api_config, get_headers


class Workflow:
    """
    The `Workflow` class is designed to interact with the `Automizor Platform` to manage
    workflow instances and facilitate the initiation of workflows based on specified
    process models and workspaces.

    This class uses environment variables for configuration, particularly to retrieve the
    API host and API token, which are essential for authenticating requests to the
    `Automizor Workflow API`. These variables are typically configured by the `Automizor Agent`.

    Required environment variable:
    - ``AUTOMIZOR_AGENT_TOKEN``: The token used for authenticating API requests.

    Example usage:

    .. code-block:: python

        from automizor import workflow

        # Start a workflow instance by name
        workflow.start_by_name("model_name", "workspace_name")
        workflow.start_by_name("model_name", "workspace_name", "BusinessKey")
        workflow.start_by_name("model_name", "workspace_name", "BusinessKey", {"initial": "data"})
    """

    _instance = None

    def __init__(self, api_token: Optional[str] = None):
        self.url, self.token = get_api_config(api_token)
        self.headers = get_headers(self.token)

    @classmethod
    def configure(cls, api_token: Optional[str] = None):
        cls._instance = cls(api_token)

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls.configure()
        return cls._instance

    def start_by_name(
        self,
        process_model: str,
        workspace: str,
        business_key: Optional[str],
        payload: Optional[bytes],
    ):
        """
        Initiates a workflow instance based on a given process model and workspace.

        Parameters:
            process_model: The name of the process model to start.
            workspace: The workspace name to which the process model belongs.
            business_key: An optional business identifier.
            payload: Optional json payload in bytes.
        """
        self._create_instance(process_model, workspace, business_key, payload)

    def _create_instance(
        self,
        process_model: str,
        workspace: str,
        business_key: Optional[str],
        payload: Optional[bytes],
    ):
        """
        Creates a new workflow instance based on a given process model and workspace.

        Parameters:
            process_model: The name of the process model to start.
            workspace: The workspace name to which the process model belongs.
            business_key: An optional business identifier.
            payload: Optional json payload in bytes.

        Raises:
            AutomizorError: If there is an error in creating the instance.
        """
        url = f"https://{self.url}/api/v1/workflow/instance/"

        data = {
            "business_key": business_key,
            "initial_data": payload,
            "process_model": process_model,
            "workspace": workspace,
        }
        response = session.post(url, headers=self.headers, data=data, timeout=60)
        if response.status_code >= 400:
            raise AutomizorError.from_response(response, "Failed to create instance")
