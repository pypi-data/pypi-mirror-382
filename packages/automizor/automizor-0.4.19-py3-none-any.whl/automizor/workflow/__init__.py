import json
from typing import Optional

from automizor.utils import JSON

from ._workflow import Workflow


def configure(api_token: str):
    """
    Configures the Worflow instance with the provided API token.
    """
    Workflow.configure(api_token)


def start_by_name(
    process_model: str,
    workspace: str,
    business_key: Optional[str] = None,
    data: Optional[JSON] = None,
):
    """
    Starts a workflow instance by process model and workspace name.

    Parameters:
        process_model: The name of the process model to start.
        workspace: The workspace name to which the process model belongs.
        business_key: An optional business identifier.
        data: Optional initial instance data.
    """
    payload = json.dumps(data or {}).encode("utf-8")

    workflow = Workflow.get_instance()
    workflow.start_by_name(process_model, workspace, business_key, payload)


__all__ = [
    "configure",
    "start_by_name",
]
