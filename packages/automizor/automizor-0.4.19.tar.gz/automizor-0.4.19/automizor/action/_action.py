from typing import Optional

from automizor import session
from automizor.exceptions import AutomizorError
from automizor.utils import JSON, get_api_config, get_headers


class Action:
    """
    The `Action` class is designed to interact with the `Automizor Platform` to run
    action based on specified action name and for a workspaces.

    This class uses environment variables for configuration, particularly to retrieve the
    API host and API token, which are essential for authenticating requests to the
    `Automizor Action API`. These variables are typically configured by the `Automizor Agent`.

    Required environment variable:
    - ``AUTOMIZOR_AGENT_TOKEN``: The token used for authenticating API requests.

    Example usage:

    .. code-block:: python

        from automizor import action

        # Run an action by name
        action.run("action_name", "workspace_name")
        action.run("action_name", "workspace_name", {"name": "John Doe"})
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

    def run(
        self,
        name: str,
        workspace: str,
        payload: Optional[bytes],
    ) -> JSON:
        """
        Runs an action using the specified action and workspace name.

        Parameters:
            name: The name of the action.
            workspace: The workspace name to which the action belongs.
            payload: Optional json payload in bytes.
        """
        return self._execute_action(name, workspace, payload)

    def _execute_action(
        self,
        name: str,
        workspace: str,
        payload: Optional[bytes],
    ) -> JSON:
        """
        Executes an action by action and workspace name.

        Parameters:
            name: The name of the action.
            workspace: The workspace name to which the action belongs.
            payload: Optional json payload in bytes.

        Raises:
            AutomizorError: If there is an error executing the action.
        """
        url = f"https://{self.url}/api/v2/action/{name}/execute?workspace={workspace}"
        response = session.put(url, headers=self.headers, data=payload, timeout=90)
        if response.status_code >= 400:
            raise AutomizorError.from_response(response, "Failed to execute action")
        return response.json()
