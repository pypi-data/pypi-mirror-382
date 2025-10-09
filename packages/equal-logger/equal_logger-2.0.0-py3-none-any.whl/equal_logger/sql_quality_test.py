import datetime as dt
import json
import os

from google.cloud import bigquery

class SqlQualityTest:

    def __init__(self, logger, cloud=None, credentials_path=None):
        """
        Initialize the SqlQualityTest instance.

        :param logger: Logger instance for logging messages.
        :param cloud: Cloud provider name ('AZURE' or 'GCP'). If not provided, the logger cloud will be used.
        :param credentials_path: Path to the JSON file with cloud credentials. If not provided, the logger credentials will be used.
        """
        self._logger = logger
        self._cloud = cloud if cloud else self._logger._cloud
        self._credentials_path = credentials_path if credentials_path else self._logger._credentials

        self._column = ""
        self._result = ""

    def _get_azure_connection_string(self):
        """
        Creates a string based on the credentials passed.
        :return: Connection string for Azure SQL Database.
        """
        with open(self._credentials_path, 'r') as file:
            creds = json.load(file)
            return (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER=tcp:{creds['SERVER']};"
                f"DATABASE={creds['DATABASE']};"
                f"UID={creds['UID']};"
                f"PWD={creds['PWD']};"
                "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
            )

    def _connect_gcp(self):
        """
        Establish a connection to Google BigQuery using service account credentials.

        :return: bigquery.Client object.
        """
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f'{self._credentials_path}'
        return bigquery.Client()

    def test_duplicate_rows(self, schema_table, column, where=False):
        """
        Test for duplicate values in a specific column of a table.

        :param schema_table: Table name with schema (e.g., 'schema.table').
        :param column: Column name to check for duplicates.
        :param where_clause: Optional WHERE condition for filtering data.
        """
        self._column = column
        where_clause = f"AND {where}" if where else ''

        query = (
            f" SELECT {column} "
            f" FROM {schema_table} "
            f" WHERE {column} IS NOT NULL {where_clause} "
            f" GROUP BY {column} "
            f" HAVING COUNT(*) > 1 "
        )
        self._run_query(
            query,
            title=f'[TEST] {schema_table} - Check Duplicates',
            success_message='OK',
            error_message='NOK: {rows} Duplicates were found on {column}',
            validation_func=self._has_zero_rows
        )

    def test_query_returns_zero_rows(self, user_query, custom_title=""):
        """
        Validate if a custom SQL query returns zero rows.

        :param user_query: SQL query string to execute.
        :param custom_title: Custom title for the validation log.
        """
        custom_title = f"{custom_title} - Free Query" if custom_title else 'Free Query'
        self._run_query(
            user_query,
            title=f'[TEST] {custom_title}',
            success_message='OK',
            error_message='NOK: {rows} returned instead of 0',
            validation_func=self._has_zero_rows
        )

    def test_temporal_null_or_zero_values(self, schema_table, date_column, evaluated_column, days: int, additional_clause=False):
        """
        Validate if a column has null or zero values within a time window.
        It's a success when the query returns rows.

        :param schema_table: Table name with schema.
        :param date_column: Date column to filter recent records.
        :param evaluated_column: Column to check for null or zero values.
        :param days: Number of days to look back.
        :param additional_clause: Additional SQL condition.
        """
        self._column = evaluated_column
        additional_clause = f"AND {additional_clause}" if additional_clause else f''
        start_date = (dt.datetime.now() - dt.timedelta(days)).strftime('%Y-%m-%d')

        query = (
            f"SELECT {evaluated_column} "
            f"FROM {schema_table} "
            f"WHERE {date_column} >= '{start_date}' {additional_clause} "
            f"AND {evaluated_column} > 0"
        )
        self._run_query(
            query,
            title=f'[TEST] {schema_table} - Temporal check',
            success_message='OK',
            error_message='NOK: {rows} rows returned on {column}',
            validation_func=self._has_rows
        )

    def test_has_data_for_each_day(self, schema_table, date_column, days, include_today=True):
        """
        Test if a table has at least one row for every day within a time window.
        :param schema_table: Table name with schema.
        :param date_column: Date column to filter recent records.
        :param days: Number of days to look back.
        :param include_today: Boolean to include today's date in the check.
        """
        self._column = date_column

        start_date = (dt.datetime.now() - dt.timedelta(days)).strftime('%Y-%m-%d')
        query = (
            f"SELECT DISTINCT({date_column}) "
            f"FROM {schema_table} "
            f"WHERE {date_column} >= '{start_date}' "
        )
        self._expected_rows = days
        if include_today:
            self._expected_rows += 1

        self._run_query(
            query=query,
            title=f'[TEST] {schema_table} - Data everyday check',
            success_message='OK',
            error_message='NOK: {rows} rows returned, more rows were expected.',
            validation_func=self._has_expected_rows
        )

    def _run_query(self, query, title, success_message, error_message, validation_func):
        """
        Execute a query and log results based on a validation function.
        Now logs the executed SQL query and total execution time.

        :param query: SQL query to execute.
        :param title: Title for logging.
        :param success_message: Message for successful validation.
        :param error_message: Message for failed validation.
        :param validation_func: Function to validate query results.
        """
        begin_time = dt.datetime.now()
        self._query = query
        try:
            is_valid = validation_func()
            duration = (dt.datetime.now() - begin_time).total_seconds()

            if is_valid:
                self._logger.success(title, f'{success_message} [Execution Time: {duration:.1f}s]')
            else:
                error_message = error_message.format(rows=self._result, column=self._column)
                self._logger.error(title, f'{error_message} [Execution Time: {duration:.1f}s]')

        except Exception as e:
            self._logger.error(title, f"Error: {e}")

    def _has_rows(self):
        """
        Check if the query result contains one or more rows.

        :return: True if there are rows, otherwise false.
        """
        self._result = self._get_cloud_result()
        return self._result > 0

    def _has_expected_rows(self):
        """
        Check if the query result contains the expected amount of rows.
        :return: True if there are rows, otherwise false.
        """
        self._result = self._get_cloud_result()
        return self._result == self._expected_rows

    def _has_zero_rows(self):
        """
        Check if the query returns rows.

        :return: True if rows exist, False if zero rows.
        """
        self._result = self._get_cloud_result()
        return self._result is None or self._result == 0

    def _get_cloud_result(self):
        """
        Execute the stored query and fetch results based on the cloud provider.

        For Azure:
            - Establishes a connection to the Azure SQL Database.
            - Executes the stored SQL query.
            - Fetches all resulting rows and returns their count.

        For GCP (Google BigQuery):
            - Establishes a connection to BigQuery.
            - Executes the stored SQL query.
            - Retrieves the result set and returns the total number of rows.

        :return: Integer representing the number of rows returned by the query.
        
        :raises ValueError: If the cloud provider is unsupported.
        :raises Exception: If any error occurs during connection or query execution.
        """
        try:
            if self._cloud == "AZURE":

                try:
                    # this import is inside this block to avoid driver errors when it's not needed
                    import pyodbc
                except:
                    raise Exception("Error importing pyodbc. Please verify the if the ODBC  driver is installed. If not, please proceed with the installation with https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server")

                conn_str = self._get_azure_connection_string()
                with pyodbc.connect(conn_str) as conn:
                    cursor = conn.cursor()
                    cursor.execute(self._query)
                    result = cursor.fetchall()
                    return len(result)

            elif self._cloud == "GCP":
                cursor = self._connect_gcp()
                job = cursor.query(self._query)
                result = job.result()
                return result.total_rows

            else:
                raise ValueError("Unsupported cloud provider.")
        except Exception as e:
            self._logger.error("Connection validation failed: ", {e})
