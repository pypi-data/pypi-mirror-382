from typing import Optional

from ._counter import Counter


def configure(api_token: str):
    """
    Configures the Counter instance with the provided API token.
    """
    Counter.configure(api_token)


def get_value(
    name: str,
) -> int:
    """
    Retrieves the current value of a counter by its name.

    Parameters:
        name: The name of the counter.
    """
    counter = Counter.get_instance()
    return counter.get_value(name)


def increment(
    name: str,
    amount: Optional[int] = 1,
    ttl: Optional[int] = 300,
) -> int:
    """
    Increments a counter by the specified amount and assigns an optional TTL.

    Parameters:
        name: The name of the counter.
        amount: The amount to increment by. Defaults to 1.
        ttl: The time-to-live in seconds for each increment. Defaults to 300 seconds.
    """
    counter = Counter.get_instance()
    return counter.increment(name, amount, ttl)


__all__ = [
    "configure",
    "get_value",
    "increment",
]
