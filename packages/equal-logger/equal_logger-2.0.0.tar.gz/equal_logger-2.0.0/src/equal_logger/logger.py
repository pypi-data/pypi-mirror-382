import datetime as dt
import hashlib
import io
import json
import time
import importlib.metadata
from random import Random
import requests

import pyarrow as pa
import pyarrow.parquet as pq

from equal_logger.integrations.azure_integration import AzureIntegration
from equal_logger.integrations.gcp_integration import GcpIntegration


class Logger:
    def __init__(self,
                 script_name: str,
                 data_source: str,
                 project: str,
                 cloud: str = '',
                 credentials: str = None,
                 webhook_password: str = None):
        """
        Initialize the Logger instance.
        :param script_name: name of the script that is running, e.g. 'script.py'
        :param data_source: name of the data source being processed, e.g. 'Meta Ads', 'Procedures', 'General'.
        :param project: name of the project that the script is part of, e.g. 'Cômodo', 'EVO Operações'.
        :param cloud: defines the cloud storage provider to use for saving logs. Options: 'GCP', 'AZURE', 'TEST', 'LOCAL'
        :param credentials: path to the JSON file with the credentials for the cloud storage provider.
        :param webhook_password: password for the webhook, if applicable.

        :attribute _RETRIES: number of retries to attempt when saving logs.
        :attribute _SLEEP_TIME: time to sleep between retries.
        :attribute _id_execucao: unique identifier for the script execution.
        :attribute _log_schema: schema for the log table.
        :attribute log_table: list of log entries.
        """
        self._version = importlib.metadata.version('equal-logger')

        self._webhook_url = "https://webhook-logger-989869946022.southamerica-east1.run.app/scripts"

        self._RETRIES = 3
        self._SLEEP_TIME = 1

        self._cloud = cloud
        self._script_name = script_name
        self._data_source = data_source
        self._project = project
        self._credentials = credentials
        self._webhook_password = webhook_password

        self._id_execucao = hashlib.md5(f'{script_name}{dt.datetime.now()}{Random().randint(1, 1000000)}'.encode()).hexdigest()
        self._log_schema = pa.schema([
            pa.field('id', pa.string()),
            pa.field('project', pa.string()),
            pa.field('cloud', pa.string()),
            pa.field('script_name', pa.string()),
            pa.field('data_source', pa.string()),
            pa.field('execution_date', pa.timestamp('ns')),
            pa.field('status', pa.string()),
            pa.field('title', pa.string()),
            pa.field('description', pa.string()),
            pa.field('extra_fields', pa.string()),
            pa.field('total_script_duration_seconds', pa.float32()),
        ])
        self.log_table = []

        self.success(title="Log", description=f"Started. [v{self._version}]")

    def _register_log(self, status, title, description, extra_fields, print_log=True):
        """
        Registers a log entry in self.log_table with the specified status, title, and description.
        :param status: can be 'ERROR', 'SUCCESS', 'INFO'
        :param title: first description of the log
        :param description: second description of the log
        :param print_log: option to print the log, default is True
        """
        log_row = {
            "id": self._id_execucao,
            "project": self._project,
            "cloud": self._cloud,
            "script_name": self._script_name,
            "data_source": self._data_source,
            "execution_date": dt.datetime.now(),
            "status": status,
            "title": str(title),
            "description": str(description),
            "extra_fields": json.dumps(extra_fields) if extra_fields else '{}',
        }

        if print_log:
            self._print_row(log_row)

        self.log_table.append(log_row)

    def _print_row(self, log_row):
        printable_json = {
            "execution_date": log_row["execution_date"],
            "status": log_row["status"],
            "title": log_row["title"]
        }
        if log_row["description"]: printable_json["description"] = log_row["description"]
        if log_row["extra_fields"] != '{}': printable_json["extra_fields"] = log_row["extra_fields"]
        print(json.dumps(printable_json, indent=2, default=str))

    def error(self, title, description='', extra_fields: dict = None, print_log=True, raise_error: Exception = None):
        """
        Logs an error entry with the specified table name and description, and prints the log.
        :param title: first description of the log
        :param description: second description of the log
        :param extra_fields: additional fields to include in the log entry
        :param print_log: option to print the log, default is True
        :param raise_error: raise an error if received
        """

        if raise_error:
            raise raise_error

        if extra_fields and not isinstance(extra_fields, dict):
            raise TypeError("extra_fields must be a dictionary")

        self._register_log("ERROR", title, description, extra_fields, print_log)

    def success(self, title, description='', extra_fields: dict = None, print_log=True):
        """
        Logs a success entry with the specified table name and description, and prints the log.
        :param title: first description of the log
        :param description: second description of the log
        :param extra_fields: additional fields to include in the log entry
        :param print_log: option to print the log, default is True
        """
        if extra_fields and not isinstance(extra_fields, dict):
            raise TypeError("extra_fields must be a dictionary")

        self._register_log("SUCCESS", title, description, extra_fields, print_log)

    def info(self, title, description='', extra_fields: dict = None, print_log=True):
        """
        Logs an info entry with the specified table name and description, and prints the log.
        :param title: first description of the log
        :param description: second description of the log
        :param extra_fields: additional fields to include in the log entry
        :param print_log: option to print the log, default is True
        """
        if extra_fields and not isinstance(extra_fields, dict):
            raise TypeError("extra_fields must be a dictionary")

        self._register_log("INFO", title, description, extra_fields, print_log)

    def _include_total_script_duration(self):
        """
        Includes a columns with the total execution time for the script,
        comparing the min timestamp with the max timestamp.
        """
        timestamps = [row['execution_date'] for row in self.log_table]
        min_timestamp = min(timestamps)
        max_timestamp = max(timestamps)
        duration_seconds = (max_timestamp - min_timestamp).total_seconds()
        for row in self.log_table:
            row['total_script_duration_seconds'] = duration_seconds

    def _get_log_table_parquet_buffer(self):
        table = pa.Table.from_pylist(self.log_table, schema=self._log_schema)
        parquet_buffer = io.BytesIO()
        pq.write_table(table, parquet_buffer, flavor='spark', compression='snappy', coerce_timestamps='ms', allow_truncated_timestamps=True)
        return parquet_buffer

    def _post_to_webhook(self, parquet_buffer):
        payload = {
            "file": parquet_buffer.getvalue(),
            "filename": f'{self._project}--{self._script_name}--{self._id_execucao}--{dt.datetime.now().strftime("%Y-%m-%d--%H-%M-%S-%f")}.parquet'
        }
        requests.post(
            self._webhook_url,
            auth=('', self._webhook_password),
            files={'file': (payload["filename"], payload["file"], 'application/octet-stream')},
            timeout=20
        ).raise_for_status()


    def save(self, raise_error=False):
        """
        Saves the log table to the cloud storage provider.
        It follows the hierarchy: logs-scripts/year=YYYY/month=MM/day=DD/script_name--YYYY-MM-DD--HH-MM-SS-ffffff.parquet

        :param raise_error: raise an error if any error log is found
        """
        self.success(title="Log", description=f"Finished [v{self._version}]", print_log=False)
        self._include_total_script_duration()

        parquet_buffer = self._get_log_table_parquet_buffer()

        for retry in range(self._RETRIES):
            try:
                if self._cloud == "GCP":
                    save_to_gcp_gcs = GcpIntegration(project=self._project, credentials_path=self._credentials, script_name=self._script_name)
                    save_to_gcp_gcs.upload_parquet_to_gcs(parquet_buffer, self._id_execucao)

                if self._cloud == "AZURE":
                    save_to_azure_adls = AzureIntegration(project=self._project, credentials_path=self._credentials, script_name=self._script_name)
                    save_to_azure_adls.upload_parquet_to_adls(parquet_buffer, self._id_execucao)

                if self._cloud == "TEST":
                    for row in self.log_table:
                        print(row)

                if self._cloud == "LOCAL":
                    with open(f'{self._script_name}--{self._id_execucao}.parquet', 'wb') as f:
                        f.write(parquet_buffer.getvalue())

                if self._webhook_password:
                    self._post_to_webhook(parquet_buffer)

                # printing the final log
                self.success(title="Log", description=f"Finished [v{self._version}]")
                break

            except Exception as e:
                print(f'Error saving logs: {e}')
                time.sleep(self._SLEEP_TIME)

        else:
            print("Error saving logs. Max retries reached.")
            if raise_error:
                raise Exception("Error saving logs. Max retries reached.")

        if raise_error:
            errors = [str(row) for row in self.log_table if row["status"] == "ERROR"]
            errors_concat = '\n'.join(errors)
            if errors:
                raise Exception(f"Erros encontrados: \n{errors_concat}")


def get_test_parquet_buffer():
    """
    :return: a parquet buffer with 60 log entries for testing purposes.
    """
    logger = Logger('GCP', 'script test', 'source test', 'project test', 'credtest')
    for _ in range(20): logger.success('test1', 'test description', print_log=False)
    for _ in range(20): logger.info('test1', 'test description', print_log=False)
    for _ in range(20): logger.error('test1', 'test description', print_log=False)
    logger.success(title="Log", description="Finished", print_log=False)
    return logger._get_log_table_parquet_buffer()
