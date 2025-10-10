"""
The module includes Pydantic types for BigQuery Connector.
"""

# Import Standard Modules
from pydantic import BaseModel, Field
from typing import Optional, Union, List


class BQClientConfig(BaseModel):
    """
    BigQuery Client configuration

    Attributes:
        project_id (str): The Google Cloud project ID.
    """

    project_id: str = Field(..., description="Project ID on Google Cloud Platform")


class BQQueryParameter(BaseModel):
    """
    BigQuery Query parameter object, including all required fields for defining the parameter

    Attributes:
        name (String): Parameter name
        type (String): Parameter type
        value (Union[str, int, float]): The value of the parameter, which
               can be a string, integer, or float.
    """

    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type according to BigQuery Python SDK")
    value: Union[str, int, float, List] = Field(..., description="Parameter value")


class BQQueryConfig(BaseModel):
    """
    BigQuery Query configuration including all elements for executing a query

    Attributes:
        query_path (String): Query file path
        query_parameters (List[BQQueryParameter]): [Optional] List of BigQuery parameters or a single parameter
        local_path (String): [Optional] Local path where to save the data
        table_name (String): [Optional] Table name
    """

    query_path: str = Field(..., description="Query file path")
    query_parameters: Optional[List[BQQueryParameter]] = Field(
        None, description="List of BigQuery parameters"
    )
    local_path: Optional[str] = Field(None, description="Local path where to save the data")
    table_name: Optional[str] = Field(None, description="Table name")

    def count_non_none_attributes(self) -> int:
        """
        Compute the number of non-None attributes

        Returns:
            (Integer): Number of non-None attributes
        """
        return sum(1 for field, value in self.__dict__.items() if value is not None)
