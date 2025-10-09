from dataclasses import asdict
from typing import Optional

from automizor import session
from automizor.exceptions import AutomizorError, NotFound
from automizor.utils import get_api_config, get_headers

from ._container import SecretContainer


class Vault:
    """
    `Vault` is a secure storage class within the `Automizor Platform` for managing
    secrets such as API keys, passwords, and other sensitive information. It offers
    functionality to securely retrieve and update secrets through direct interaction
    with the `Automizor API`.

    Configuration for accessing and manipulating these secrets is driven by environment
    variables, which are essential for specifying the API's host and token for
    authentication purposes.

    Environment variables requisite for operation include:
    - ``AUTOMIZOR_AGENT_TOKEN``: The token for authenticating against the `Automizor API`.

    Example usage:

    .. code-block:: python

        from automizor import vault

        # Create a new secret
        vault.create_secret("my_secret", {"username": "admin", "password": "*****"})

        # Retrieve a secret by its name
        secret = vault.get_secret("my_secret")
        print(secret.get("username"))  # Output: "admin"
        print(secret.get("password"))  # Output: "*****"

        # Update a existing secret
        secret = vault.get_secret("my_secret")
        secret.update({"username": "user"})
        vault.set_secret(secret)
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

    def create_secret(self, secret: SecretContainer) -> SecretContainer:
        """
        Creates a new secret. Stores the secret in the `Automizor API`.
        If the secret already exists, it will be updated.

        Args:
            secret: The secret to create.

        Returns:
            The created secret.

        Raises:
            AutomizorVaultError: If creating the secret fails.
        """

        try:
            return self._update_secret(secret)
        except NotFound:
            return self._create_secret(secret)

    def get_secret(self, name) -> SecretContainer:
        """
        Retrieves a secret by its name. Fetches from the `Automizor API`.

        Args:
            name: The name of the secret to retrieve.

        Returns:
            The retrieved secret.

        Raises:
            AutomizorVaultError: If retrieving the secret fails.
        """

        return self._get_secret(name)

    def set_secret(self, secret: SecretContainer) -> SecretContainer:
        """
        Updates an existing secret. Updates to the `Automizor API`.

        Args:
            secret: The secret to update.

        Returns:
            The updated secret.

        Raises:
            AutomizorVaultError: If updating the secret fails.
        """

        return self._update_secret(secret)

    def _create_secret(self, secret: SecretContainer) -> SecretContainer:
        url = f"https://{self.url}/api/v1/vault/secret/"
        response = session.post(
            url, headers=self.headers, timeout=60, json=asdict(secret)
        )
        if response.status_code >= 400:
            raise AutomizorError.from_response(response, "Failed to create secret")
        return SecretContainer(**response.json())

    def _get_secret(self, name: str) -> SecretContainer:
        url = f"https://{self.url}/api/v1/vault/secret/{name}/"
        response = session.get(url, headers=self.headers, timeout=60)
        if response.status_code >= 400:
            raise AutomizorError.from_response(response, "Failed to get secret")
        return SecretContainer(**response.json())

    def _update_secret(self, secret: SecretContainer) -> SecretContainer:
        url = f"https://{self.url}/api/v1/vault/secret/{secret.name}/"
        response = session.put(
            url, headers=self.headers, timeout=60, json=asdict(secret)
        )
        if response.status_code >= 400:
            raise AutomizorError.from_response(response, "Failed to update secret")
        return SecretContainer(**response.json())
