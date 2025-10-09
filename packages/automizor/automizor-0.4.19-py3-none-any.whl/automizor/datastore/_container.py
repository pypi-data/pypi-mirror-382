from dataclasses import dataclass

from automizor.utils import JSON


@dataclass
class DataStoreContainer:
    """
    The `DataStoreContainer` is a wrapper around the data store that
    provides a get and set method to interact with the data store.

    Attributes:
        datastore: The data store.
        name: The name of the data store.
    """

    from ._datastore import DataStore

    datastore: DataStore
    name: str

    def get(self, primary_key=None, secondary_key=None):
        """Get values from the datastore."""
        return self.datastore.get_values(self.name, primary_key, secondary_key)

    def set(self, values: JSON):
        """Set values in the datastore."""
        self.datastore.set_values(self.name, values)
