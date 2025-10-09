import json
from typing import Optional

from automizor.utils import JSON

from ._action import Action


def configure(api_token: str):
    """
    Configures the Action instance with the provided API token.
    """
    Action.configure(api_token)


def run(
    name: str,
    workspace: str,
    data: Optional[JSON] = None,
) -> JSON:
    """
    Runs an action using the specified action and workspace name.

    Parameters:
        name: The name of the action.
        workspace: The workspace name to which the action belongs.
        data: Optional action payload data.
    """
    payload = json.dumps(data or {}).encode("utf-8")

    action = Action.get_instance()
    return action.run(name, workspace, payload)


__all__ = [
    "configure",
    "run",
]
