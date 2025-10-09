import os
import platform
from typing import Dict, List, Optional, Union

from automizor import version
from automizor.exceptions import AutomizorError

JSON = Union[str, int, float, bool, None, Dict[str, "JSON"], List["JSON"]]


OS_SYSTEM, OS_RELEASE, _ = platform.system_alias(
    platform.system(), platform.release(), platform.version()
)


def get_api_config(api_token: Optional[str] = None) -> tuple[str, str]:
    if api_token is None:
        api_token = os.getenv("AUTOMIZOR_AGENT_TOKEN")

        if not api_token:
            raise AutomizorError("AUTOMIZOR_AGENT_TOKEN is not set.")

    try:
        token, url = api_token.strip().split("@")
    except ValueError as exc:
        raise AutomizorError("The API token is not in the correct format.") from exc
    return url, token


def get_headers(token: str) -> dict:
    return {
        "Authorization": f"Token {token}",
        "User-Agent": f"Automizor/{version} {OS_SYSTEM}/{OS_RELEASE}",
    }
