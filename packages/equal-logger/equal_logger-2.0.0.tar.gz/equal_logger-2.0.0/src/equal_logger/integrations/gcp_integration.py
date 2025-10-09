import datetime as dt

from google.cloud import storage


def get_storage_logs_script_path(script_name, log_id):
    """
    Returns the path for the new file following the logs structure.
    :param script_name: name of the script to name the parquet file
    :return: string with the path for the new file
    """
    today = dt.datetime.now()
    return (f'logs_scripts/'
            f'year={today.strftime("%Y")}/'
            f'month={today.strftime("%m")}/'
            f'day={today.strftime("%d")}/'
            f'{script_name}--{log_id}--{today.strftime("%Y-%m-%d--%H-%M-%S-%f")}.parquet')


class GcpIntegration:

    def __init__(self, project, script_name, credentials_path):
        """
        Initiates the GcpIntegration instance.
        :param project: name of the project to locate the bucket
        :param script_name: name of the script to name the parquet file
        :param credentials_path: optional path to the JSON file with the GCP credentials
        """
        self._script_name = script_name
        self._credentials_path = credentials_path
        if credentials_path:
            self._storage_client = storage.Client.from_service_account_json(credentials_path)
        else:
            self._storage_client = storage.Client()
        self._bucket = self._storage_client.bucket(f'logs-equal-{project}')

    def upload_parquet_to_gcs(self, parquet_buffer, log_id):
        """
        Uploads a parquet file to Google Cloud Storage.
        """
        path = get_storage_logs_script_path(self._script_name, log_id)
        blob = self._bucket.blob(path)
        parquet_buffer.seek(0)
        blob.upload_from_file(parquet_buffer, content_type='application/octet-stream')
