from dataclasses import dataclass, fields
from typing import Any, Dict


def ignore_extra_fields(cls):
    original_post_init = getattr(cls, "__post_init__", None)

    def __init__(self, **kwargs):
        cls_fields = {field.name: field for field in fields(cls)}
        for name, value in kwargs.items():
            if name in cls_fields:
                setattr(self, name, value)
        if original_post_init:
            original_post_init(self)

    setattr(cls, "__init__", __init__)
    return cls


@ignore_extra_fields
@dataclass
class SecretContainer:
    """
    Represents a secret, comprising a name and its associated values.

    Attributes:
        description: A description of the secret.
        name: The name of the secret.
        value: The secret's values, stored in a dictionary as key-value pairs.
    """

    name: str
    value: Dict[str, Any]
    description: str = ""

    def get(self, key, default=None):
        """Return the value for key if key is in the dictionary, else default."""
        return self.value.get(key, default)

    def items(self):
        """Secret.items() -> a set-like object providing a view on secret's items."""
        return self.value.items()

    def keys(self):
        """Secret.keys() -> a set-like object providing a view on secret's keys."""
        return self.value.keys()

    def update(self, pairs: Dict[str, Any]):
        """Update the secret's dictionary with the key-value pairs from pairs."""
        self.value.update(pairs)

    def __getitem__(self, key):
        return self.value[key]

    def __setitem__(self, key, value):
        self.value[key] = value

    def __contains__(self, key):
        return key in self.value

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        keys = ", ".join(self.keys())
        return f"Secret(name={self.name}, keys=[{keys}])"
