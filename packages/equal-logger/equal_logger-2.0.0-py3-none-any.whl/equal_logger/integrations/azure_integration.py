import datetime as dt
import json
from azure.storage.filedatalake import DataLakeServiceClient

TODAY = dt.datetime.now()


def get_storage_logs_script_path():
    return (f'logs-scripts/'
            f'year={TODAY.strftime("%Y")}/'
            f'month={TODAY.strftime("%m")}/'
            f'day={TODAY.strftime("%d")}')


class AzureIntegration:

    def __init__(self, project, script_name, credentials_path):
        """
        Initialize the AzureIntegration instance.

        :param project: Project name to build the file system name.
        :param script_name: Name of the script using this uploader.
        :param credentials_path: Path to the JSON file with Azure credentials.
        """
        self._script_name = script_name
        self._load_credentials(credentials_path)
        self._file_system_name = f'logs-equal-{project}'
        self._connect_str = (
            f"DefaultEndpointsProtocol=https;AccountName={self._account_name};"
            f"AccountKey={self._account_key};EndpointSuffix=core.windows.net"
        )

        self._service_client = DataLakeServiceClient.from_connection_string(self._connect_str)
        self._file_system_client = self._service_client.get_file_system_client(file_system=self._file_system_name)

    def _load_credentials(self, credentials_path):
        """
        Load Azure credentials from a JSON file.

        :param credentials_path: Path to the JSON credentials file or the token already loaded in dict format.
        """
        if type(credentials_path) is not dict:
            with open(credentials_path, 'r') as file:
                credentials_path = json.load(file)

        self._account_name = credentials_path['AccountName']
        self._account_key = credentials_path['AccountKey']

    def upload_parquet_to_adls(self, parquet_buffer, log_id):
        """
        Uploads a parquet file to Azure Data Lake Storage.

        :param parquet_buffer:
        """
        file_path = get_storage_logs_script_path()
        full_file_name = f"{self._script_name}--{log_id}--{TODAY.strftime('%Y-%m-%d--%H-%M-%S-%f')}.parquet"

        directory_client = self._file_system_client.get_directory_client(file_path)
        file_client = directory_client.create_file(full_file_name)

        parquet_buffer.seek(0)
        file_client.upload_data(parquet_buffer.read(), overwrite=True)