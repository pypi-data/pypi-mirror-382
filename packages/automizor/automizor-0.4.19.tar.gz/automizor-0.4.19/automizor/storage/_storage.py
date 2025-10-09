from typing import List, Optional

from automizor import session
from automizor.exceptions import AutomizorError, NotFound
from automizor.utils import JSON, get_api_config, get_headers


class Storage:
    """
    `Storage` is a class designed to interact with the `Automizor Platform` for managing
    digital assets, facilitating the retrieval of files in various formats such as bytes,
    files, JSON, and text. It leverages the `Automizor Storage API` to access and download
    these assets securely.

    This class utilizes environment variables for configuration, specifically for setting
    up the API host and API token, which are essential for authenticating requests made
    to the `Automizor Storage API`. These variables are typically configured by the
    `Automizor Agent`.

    To use this class effectively, ensure that the following environment variables are
    set in your environment:

    - ``AUTOMIZOR_AGENT_TOKEN``: The token for authenticating against the `Automizor API`.

    Example usage:

    .. code-block:: python

        from automizor import storage

        # To list all assets
        asset_names = storage.list_assets()

        # To delete an asset
        storage.delete_asset("asset_name")

        # Save an asset
        storage.set_bytes("asset_name", b"Hello, World!")
        storage.set_file("asset_name", "/path/to/file")
        storage.set_json("asset_name", {"key": "value"})
        storage.set_text("asset_name", "Hello, World!")

        # Get an asset
        bytes_data = storage.get_bytes("asset_name")
        file_path = storage.get_file("asset_name", "/path/to/save/file")
        json_data = storage.get_json("asset_name")
        text_data = storage.get_text("asset_name")
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

    def list_assets(self) -> List[str]:
        """
        Retrieves a list of all asset names.

        This function fetches the names of all assets stored in the storage service,
        providing a convenient way to list and identify the available assets.

        Returns:
            A list of all asset names.
        """
        url = f"https://{self.url}/api/v1/storage/asset/"
        asset_names = []

        while url:
            response = session.get(url, headers=self.headers, timeout=60)
            if response.status_code >= 400:
                raise AutomizorError.from_response(response, "Failed to list assets")
            data = response.json()

            for asset in data["results"]:
                asset_names.append(asset["name"])
            url = data["next"]
        return asset_names

    def delete_asset(self, name: str):
        """
        Deletes the specified asset.

        This function deletes the asset identified by `name` from the storage service.
        It is useful for removing assets that are no longer needed or should be cleaned
        up to free up storage space.

        Parameters:
            name: The name identifier of the asset to delete.
        """

        url = f"https://{self.url}/api/v1/storage/asset/{name}/"
        response = session.delete(url, headers=self.headers, timeout=60)
        if response.status_code >= 400:
            raise AutomizorError.from_response(response, "Failed to delete asset")

    def get_bytes(self, name: str) -> bytes:
        """
        Retrieves the specified asset as raw bytes.

        This function fetches the asset identified by `name` from the storage service
        and returns it as a byte stream. It is useful for binary files or for data
        that is intended to be processed or stored in its raw form.

        Parameters:
            name: The name identifier of the asset to retrieve.

        Returns:
            The raw byte content of the asset.
        """

        return self._download_file(name, mode="content")

    def get_file(self, name: str, path: str) -> str:
        """
        Downloads the specified asset and saves it to a file.

        This function fetches the asset identified by `name` and saves it directly
        to the filesystem at the location specified by `path`. It is useful for
        downloading files that need to be preserved in the file system, such as
        documents, images, or other files.

        Parameters:
            name: The name identifier of the asset to retrieve.
            path: The filesystem path where the file will be saved.

        Returns:
            The path to the saved file, confirming the operation's success.
        """

        content = self._download_file(name, mode="content")
        with open(path, "wb") as file:
            file.write(content)
        return path

    def get_json(self, name: str) -> JSON:
        """
        Retrieves the specified asset and parses it as JSON.

        This function fetches the asset identified by `name` from the storage service
        and parses it as JSON. It is useful for assets stored in JSON format, allowing
        for easy access and manipulation of structured data.

        Parameters:
            name: The name identifier of the asset to retrieve.

        Returns:
            The parsed JSON data, which can be a dict, list, or primitive data type.
        """

        return self._download_file(name, mode="json")

    def get_text(self, name: str) -> str:
        """
        Retrieves the specified asset as a text string.

        This function fetches the asset identified by `name` from the storage service
        and returns it as a text string. It is useful for text-based files, such as
        configuration files, CSVs, or plain text documents.

        Parameters:
            name: The name identifier of the asset to retrieve.

        Returns:
            The content of the asset as a text string.
        """

        return self._download_file(name, mode="text")

    def set_bytes(self, name: str, content: bytes, content_type: str):
        """
        Uploads the specified content as a new asset.

        This function uploads the provided `content` as a new asset with the specified
        `name`. It is useful for creating new assets or updating existing ones with
        fresh content.

        Parameters:
            name: The name identifier of the asset to create.
            content: The raw byte content of the asset.
            content_type: The MIME type of the asset content.
        """

        try:
            self._update_asset(name, content, content_type)
        except NotFound:
            self._create_asset(name, content, content_type)

    def _create_asset(self, name: str, content: bytes, content_type: str):
        """
        Creates a new asset with the specified content.

        This function creates a new asset with the specified `name` and `content` in the
        storage service. It is useful for uploading new assets or updating existing ones
        with fresh content.

        Parameters:
            name: The name identifier of the asset to create.
            content: The raw byte content of the asset.
            content_type: The MIME type of the asset content.
        """

        url = f"https://{self.url}/api/v1/storage/asset/"
        data = {"content_type": content_type, "name": name}
        files = {"file": ("text.txt", content, content_type)}
        response = session.post(
            url, headers=self.headers, files=files, data=data, timeout=60
        )
        if response.status_code >= 400:
            raise AutomizorError.from_response(response, "Failed to create asset")

    def _download_file(self, name: str, mode: str = "content"):
        url = self._get_asset_url(name)
        response = session.get(url=url, timeout=60)
        if response.status_code >= 400:
            raise AutomizorError.from_response(response, "Failed to download asset")

        match mode:
            case "content":
                return response.content
            case "json":
                return response.json()
            case "text":
                return response.text
        raise RuntimeError(f"Invalid mode {mode}")

    def _get_asset_url(self, name: str) -> str:
        url = f"https://{self.url}/api/v1/storage/asset/{name}/"
        response = session.get(url, headers=self.headers, timeout=60)
        if response.status_code >= 400:
            raise AutomizorError.from_response(response, "Failed to get asset URL")

        url = response.json().get("file")
        if url:
            return url
        raise RuntimeError("Url not found")

    def _update_asset(self, name: str, content: bytes, content_type: str):
        """
        Updates the specified asset with new content.

        This function updates the asset identified by `name` with fresh content
        provided as `content`. It is useful for modifying existing assets without
        creating a new asset, ensuring that the asset's content is up-to-date.

        Parameters:
            name: The name identifier of the asset to update.
            content: The raw byte content of the asset.
            content_type: The MIME type of the asset content.
        """

        url = f"https://{self.url}/api/v1/storage/asset/{name}/"
        data = {"content_type": content_type, "name": name}
        files = {"file": ("text.txt", content, content_type)}
        response = session.put(
            url, headers=self.headers, files=files, data=data, timeout=60
        )
        if response.status_code >= 400:
            raise AutomizorError.from_response(response, "Failed to update asset")
