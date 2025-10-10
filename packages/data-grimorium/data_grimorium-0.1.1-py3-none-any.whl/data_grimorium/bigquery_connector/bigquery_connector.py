"""
Defines a Connector class in order to
interact with BigQuery datasets and tables.
"""

# Import Standard Modules
import logging
from pathlib import Path
from typing import Union, List
import pandas as pd
from google.cloud import bigquery

# Import Package Modules
from data_grimorium.bigquery_connector.bigquery_types import (
    BQClientConfig,
    BQQueryParameter,
    BQQueryConfig,
)
from data_grimorium.general_utils.general_utils import read_file_from_path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class BigQueryConnector:
    """
    The class implements a BigQuery Connector
    in order to query datasets and tables

    Attributes:
        _root_path (pathlib.Path): Root path of the project
        _client_config (BQClientConfig): Configurations for instance a BigQuery Client instance
        _client (bigquery.Client): BigQuery client object

    Methods:
        execute_query_from_config: Execute a query from local path and with a certain set of parameter configurations.
        table_exists: Check if a table exists in a dataset
        wrap_dictionary_to_query_config: Converts a dictionary of Query Configurations into a ``BQQueryConfig`` object.
    """

    def __init__(self, client_config: BQClientConfig, root_path: Path):
        """
        Constructor of the class BigqueryConnector

        Args:
            client_config (BQClientConfig): Config for instance a BigQuery Client
            root_path (Path): Root path to the project
        """
        # Initialise attributes
        self._client_config = client_config
        self._root_path = root_path

        # Set the client
        self._set_client()

    def _set_client(self):
        """
        Set the attribute ``_client`` with an instance of the BigQuery Client.
        """
        logging.info(
            f"💼 Set the BigQuery client with project id {self._client_config.project_id.value}"
        )

        # Set the client
        self._client = bigquery.Client(project=self._client_config.project_id.value)

    @staticmethod
    def _build_query_parameters(
        query_parameters: List[BQQueryParameter],
    ) -> List[Union[bigquery.ArrayQueryParameter, bigquery.ScalarQueryParameter]]:
        """
        Build BigQuery query parameters from a list of BQQueryParameter

        Args:
            query_parameters (List[BQQueryParameter]): Query parameters

        Returns:
            (List[Union[ArrayQueryParameter, ScalarQueryParameter]]):
            BigQuery list of parameters
        """

        # Initialise empty list BigQuery query parameters
        bigquery_query_parameters = []

        # Fetch all query parameters
        for query_parameter in query_parameters:
            # Check if the ScalarQueryParameter or ArrayQueryParameter is required
            # The difference is in the type of values passed (No list: scalar, list: array)
            if isinstance(query_parameter.value, list):
                # Build the parameter
                bigquery_parameter = bigquery.ArrayQueryParameter(
                    *query_parameter.__dict__.values()
                )
            else:
                # Build the parameter
                bigquery_parameter = bigquery.ScalarQueryParameter(
                    *query_parameter.__dict__.values()
                )

            # Append to the list of parameters
            bigquery_query_parameters.append(bigquery_parameter)

        return bigquery_query_parameters

    def execute_query_from_config(self, query_config: BQQueryConfig) -> Union[pd.DataFrame, bool]:
        """
        Execute a query from local path and with a certain set of parameter configurations.
        The query can either read data or create a table on BigQuery.

        Args:
            query_config (BQQueryConfig): Query configurations (path and parameters)

        Returns:
            result (Union[pd.DataFrame, bool]): The result of the query execution.

                  - pd.DataFrame: When the query is executed successfully and returns data.

                  - bool: `True` if the query executes successfully but does not return data
        """
        # Initialise result to return
        result = None

        # Retrieve query path
        query_path = Path(query_config.query_path)

        # Read query
        query = read_file_from_path(query_path, self._root_path)

        # Check if there are parameters
        if query_config.query_parameters is None:
            # Execute the job in BigQuery
            job = self._client.query(query)
        else:
            # Retrieve BigQuery query parameters
            parameters = self._build_query_parameters(query_config.query_parameters)

            # Execute the job BigQuery with parameters
            job = self._client.query(
                query=query,
                job_config=bigquery.QueryJobConfig(query_parameters=parameters),
            )

        # Extract the job result
        result = job.result()

        # Switch between a read query and a table creation query
        if job.statement_type == "CREATE_TABLE_AS_SELECT":
            # Return table creation status
            result = job.done()

            logging.info("✅ Table created")

        else:
            # Convert data to a Pandas DataFrame
            result = result.to_dataframe()

            logging.info(f"✅ Retrieved {len(result)} rows")

        return result

    def table_exists(self, table_name: str, dataset_name: str) -> bool:
        """
        Check if a table exists in a dataset.

        Args:
            table_name (str): Name of the table
            dataset_name (str): Name of the dataset

        Returns:
            (bool): Flag indicating if the table exists
        """
        logging.info(f"🗂️ Retrieve list of tables in dataset: {dataset_name}")

        # Retrieve the list of tables
        tables = self._client.list_tables(dataset_name)

        # Retrieve the list of table names
        table_names = [table.table_id for table in tables]

        # Check if the table exists
        exists = table_name in table_names

        if exists:
            logging.info(f"✅ Table {table_name} exists in dataset {dataset_name}")
        else:
            logging.info(f"❌ Table {table_name} does not exist in dataset {dataset_name}")

        return exists

    @staticmethod
    def wrap_dictionary_to_query_config(query_config_dictionary: dict) -> BQQueryConfig:
        """
        Converts a dictionary of Query Configurations into a ``BQQueryConfig`` object.

        Args:
            query_config_dictionary (dict): The dictionary containing Query Configurations.

        Returns:
            (BQQueryConfig): Object with BigQuery query configurations.
        """
        # Check if there are parameters
        if "query_parameters" not in query_config_dictionary.keys():
            logging.info("⚠️ No query parameters")
        else:
            logging.info("✅ Wrapping query parameters")

            # Retrieve parameters
            query_parameters = query_config_dictionary["query_parameters"]

            # Wrap query parameters
            wrapped_parameters = [
                BQQueryParameter(**param_dict) for param_dict in query_parameters.values()
            ]

            # Update the dictionary with the wrapped parameters
            query_config_dictionary["query_parameters"] = wrapped_parameters

        # Wrap into the object
        query_config = BQQueryConfig(**query_config_dictionary)

        return query_config
