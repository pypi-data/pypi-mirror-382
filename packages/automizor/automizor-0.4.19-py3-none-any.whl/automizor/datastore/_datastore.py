from typing import Optional

from automizor import session
from automizor.exceptions import AutomizorError
from automizor.utils import JSON, get_api_config, get_headers


class DataStore:
    """
    `DataStore` is a class designed to interface with the `Automizor Platform`
    to manage and manipulate data stored in various formats. It supports
    operations to retrieve and update data using a unified API.

    The class initializes an HTTP request with the necessary headers for
    authentication, and provides methods to retrieve values, and set values in
    the store.
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

    def get_values(
        self,
        name: str,
        primary_key: Optional[str] = None,
        secondary_key: Optional[str] = None,
    ) -> JSON:
        """
        Retrieves values from the specified data store.

        Parameters:
            name (str): The name of the data store.
            primary_key (str, optional): The primary key for the values.
            secondary_key (str, optional): The secondary key for the values.

        Returns:
            JSON: The values from the data store.
        """

        return self._get_values(name, primary_key, secondary_key)

    def set_values(self, name: str, values: JSON) -> None:
        """
        Sets values in the specified data store.

        Parameters:
            name (str): The name of the data store.
            values (JSON): The values to set in the data store.
        """

        return self._set_values(name, values)

    def _get_values(
        self,
        name: str,
        primary_key: Optional[str] = None,
        secondary_key: Optional[str] = None,
    ) -> JSON:
        params = (
            {"primary_key": primary_key, "secondary_key": secondary_key}
            if primary_key or secondary_key
            else {}
        )
        url = f"https://{self.url}/api/v1/workflow/datastore/{name}/values/"
        response = session.get(url, headers=self.headers, params=params, timeout=60)
        if response.status_code >= 400:
            raise AutomizorError.from_response(
                response, "Failed to get datastore values"
            )

        return response.json()

    def _set_values(self, name: str, values: JSON) -> None:
        url = f"https://{self.url}/api/v1/workflow/datastore/{name}/values/"
        response = session.post(url, headers=self.headers, json=values, timeout=60)
        if response.status_code >= 400:
            raise AutomizorError.from_response(
                response, "Failed to set datastore values"
            )
