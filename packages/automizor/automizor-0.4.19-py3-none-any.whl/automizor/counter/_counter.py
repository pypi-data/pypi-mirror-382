from typing import Optional

from automizor import session
from automizor.exceptions import AutomizorError
from automizor.utils import get_api_config, get_headers


class Counter:
    """
    The `Counter` class is designed to interact with the `Automizor Platform`
    to manage named counters within a workspace.

    This class provides methods for retrieving and incrementing counters
    through the Automizor Counter API. It uses environment variables for
    configuration, particularly to obtain the API host and API token required
    for authenticating requests. These values are typically set automatically
    by the `Automizor Agent`.

    Required environment variable:
    - ``AUTOMIZOR_AGENT_TOKEN``: The token used for authenticating API requests.

    Example usage:

    .. code-block:: python

        from automizor import counter

        # Increment a counter by name
        counter.increment("foo", amount=3, ttl=60)

        # Get a counter value by name
        counter.get_value("foo")
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

    def get_value(
        self,
        name: str,
    ):
        """
        Retrieves the current value of the specified counter.

        Parameters:
            name: The name of the counter.

        Returns:
            The current integer value of the counter.

        Raises:
            AutomizorError: If the counter value could not be retrieved.
        """
        return self._get_value(name)

    def increment(
        self,
        name: str,
        amount: Optional[int] = 1,
        ttl: Optional[int] = 300,
    ) -> int:
        """
        Increments a counter by the specified amount with an optional TTL.

        Parameters:
            name: The name of the counter.
            amount: The amount to increment by. Defaults to 1.
            ttl: The time-to-live in seconds for each increment entry. Defaults to 300.
        """
        return self._increment_counter(name, amount, ttl)

    def _get_value(
        self,
        name: str,
    ) -> int:
        """
        Internal helper method for fetching the current counter value
        from the Automizor Counter API.

        Parameters:
            name: The name of the counter.

        Raises:
            AutomizorError: If there is an error retrieving the counter.
        """
        url = f"https://{self.url}/api/v2/counter/{name}"
        response = session.get(url, headers=self.headers, timeout=60)
        if response.status_code >= 400:
            raise AutomizorError.from_response(response, "Failed to get counter value")
        return response.json()

    def _increment_counter(
        self,
        name: str,
        amount: int,
        ttl: int,
    ) -> int:
        """
        Internal helper method for incrementing a counter through the
        Automizor Counter API.

        Parameters:
            name: The name of the counter.
            amount: The amount to increment by.
            ttl: The time-to-live in seconds for each increment entry.

        Raises:
            AutomizorError: If there is an error incrementing the counter.
        """
        url = f"https://{self.url}/api/v2/counter/{name}?amount={amount}&ttl={ttl}"
        response = session.put(url, headers=self.headers, timeout=60)
        if response.status_code >= 400:
            raise AutomizorError.from_response(response, "Failed to increment counter")
        return response.json()
