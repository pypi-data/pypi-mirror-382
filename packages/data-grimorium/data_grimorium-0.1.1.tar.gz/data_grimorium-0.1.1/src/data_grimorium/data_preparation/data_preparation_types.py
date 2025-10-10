"""
This module includes Pydantic types for the whole project
"""

# Import Standard Modules
from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel, Field


class SentenceTransformersConfig(BaseModel):
    """
    Configuration for embedding generation with SentenceTransformers library

    Attributes:
        model_name (str): The name of the model to use
        numpy_tensor (Boolean): Output tensor to be a numpy array
    """

    model_name: str = Field("all-MiniLM-L6-v2", description="Model name")
    numpy_tensor: bool = Field(False, description="Output tensor to be a numpy array")


class EmbeddingsConfig(BaseModel):
    """
    Configuration for an embedding generation model

    Attributes:
        method (str): The embedding approach to use (e.g., SentenceTransformer)
        embedding_model_config (Union[SentenceTransformersConfig]): Model configuration
    """

    method: str = Field("SentenceTransformer", description="Embedding approach to use")
    embedding_model_config: Union[SentenceTransformersConfig] = Field(
        ..., description="Model configuration"
    )


class PCAConfig(BaseModel):
    """
    Configuration for a PCA model

    Attributes:
        n_components (Integer): Number of components
    """

    n_components: int = Field(..., description="Number of components")


class CompressEmbeddingsConfig(BaseModel):
    """
    Configuration for compressing embeddings model

    Attributes:
        method (str): The compress approach to use (e.g., PCA)
        compress_model_config (Union[PCAConfig]): Model configuration
    """

    method: str = Field("PCA", description="Compress approach to use")
    compress_model_config: Union[PCAConfig] = Field(..., description="Model configuration")


class EncodingTextConfig(BaseModel):
    """
    Configuration to encode Text and compress them into a lower
    dimensional vector

    Attributes:
        embeddings_config (EmbeddingsConfig): Configuration for embedding generation
        compress_embeddings_config (CompressEmbeddingsConfig): Configuration for embedding compression
    """

    embeddings_config: EmbeddingsConfig = Field(
        ..., description="Configuration for embedding generation"
    )
    compress_embeddings_config: CompressEmbeddingsConfig = Field(
        ..., description="Configuration for embedding compression"
    )


class DateExtractionConfig(BaseModel):
    """
    Configuration to extract information from a date field

    Attributes:
        column_name (str): Column name containing the date
        extract_year (Boolean): Flag to indicate to extract the year
        extract_month (Boolean): Flag to indicate to extract the month
    """

    column_name: str = Field(..., description="Column name containing the date")
    extract_year: bool = Field(..., description="Flag to indicate to extract the year")
    extract_month: bool = Field(..., description="Flag to indicate to extract the month")


class StandardisationMethod(str, Enum):
    MIN_MAX = "min_max_scaler"
    STANDARD = "standard_scaler"


class OutlierMethod(str, Enum):
    Z_SCORE = "z_score"
    IQR = "iqr"


class NanStrategy(str, Enum):
    DROP = "drop_nan"
    IMPUTE = "simple_imputer"


class OutlierConfig(BaseModel):
    """
    Configuration for drop outlier transformation

    Attributes:
        method (Optional[OutlierMethod]): Outlier removal method to use
        n_std (Optional[int]): Number of standard deviations to use
    """

    method: Optional[OutlierMethod] = Field(None, description="Outlier removal method to use")
    n_std: Optional[int] = Field(None, description="Number of standard deviations to use")


class NumericalFeaturesConfig(BaseModel):
    """
    Configuration for numerical features transformation

    Attributes:
        column_name (str): Name of the numerical column to process
        standardisation (Optional[StandardisationMethod]): Standardisation method to apply
        drop_outliers (Optional[OutlierMethod]): Outlier removal method to use
        nan_values (Optional[NanStrategy]): Strategy to handle missing values
    """

    column_name: str = Field(..., description="Name of the numerical column to process")
    standardisation: Optional[StandardisationMethod] = Field(
        None, description="Standardisation method to apply"
    )
    drop_outliers: Optional[OutlierConfig] = Field(
        None, description="Outlier removal configuration to use"
    )
    nan_values: Optional[NanStrategy] = Field(None, description="Strategy to handle missing values")


class FlagFeatureConfig(BaseModel):
    """
    Configuration for flag features transformation

    Attributes:
        column_name (str): Name of the numerical column to process
        output_column_name (str): Name of the output column
    """

    column_name: str = Field(..., description="Name of the column to process")
    output_column_name: str = Field(..., description="Name of the output column")
