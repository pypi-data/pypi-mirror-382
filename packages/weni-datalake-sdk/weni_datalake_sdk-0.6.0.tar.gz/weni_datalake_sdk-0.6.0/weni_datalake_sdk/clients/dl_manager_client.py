import requests

from weni_datalake_sdk.paths.validator import validate_path
from weni_datalake_sdk.utils.exceptions import DLManagerError


class DLManagerClient:
    """
    Client to communicate with DL Manager.
    """

    def __init__(self, base_url="https://dl-manager.example.com/api"):
        self.base_url = base_url

    def insert(self, path_class, data: dict):
        """
        Send data DL Manager via API HTTP.
        """
        validate_path(path_class)

        payload = {"data": data}

        try:
            response = requests.post(
                f"{self.base_url}/{path_class.get_table_name()}/send",
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise DLManagerError(f"Error on send data to DL Manager: {e}")

        return response.json()
