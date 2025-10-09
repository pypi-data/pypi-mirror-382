from typing import Any, Dict

from ._container import SecretContainer
from ._vault import Vault


def configure(api_token: str):
    """
    Configures the Vault instance with the provided API token.
    """
    Vault.configure(api_token)


def create_secret(
    name: str,
    value: Dict[str, Any],
    description: str = "",
) -> SecretContainer:
    """
    Creates a new secret. Stores the secret in the `Automizor API`.
    If the secret already exists, it will be updated.

    Args:
        name: The name of the secret.
        value: The value of the secret.
        description: The description of the secret.

    Returns:
        The created secret.

    Raises:
        AutomizorVaultError: If creating the secret fails.
    """

    secret = SecretContainer(
        name=name,
        description=description,
        value=value,
    )

    vault = Vault.get_instance()
    return vault.create_secret(secret)


def get_secret(name: str) -> SecretContainer:
    """
    Retrieves a secret by its name. Fetches from the `Automizor API`.

    Args:
        name: The name of the secret to retrieve.

    Returns:
        The retrieved secret.

    Raises:
        AutomizorVaultError: If retrieving the secret fails.
    """

    vault = Vault.get_instance()
    return vault.get_secret(name)


def set_secret(secret: SecretContainer) -> SecretContainer:
    """
    Updates an existing secret. Updates to the `Automizor API`.

    Args:
        secret: The secret to update.

    Returns:
        The updated secret.

    Raises:
        AutomizorVaultError: If updating the secret fails.
    """

    vault = Vault.get_instance()
    return vault.set_secret(secret)


__all__ = [
    "SecretContainer",
    "configure",
    "create_secret",
    "get_secret",
    "set_secret",
]
