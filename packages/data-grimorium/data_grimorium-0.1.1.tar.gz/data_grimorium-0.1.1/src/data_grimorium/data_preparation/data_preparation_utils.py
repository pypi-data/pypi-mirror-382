"""
The module includes functions for implementing data transformations
"""

# Import Standard Libraries
import numpy as np
import pandas as pd
import logging
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import zscore
from typing import List

# Import Package Modules
from data_grimorium.data_preparation.data_preparation_types import (
    EmbeddingsConfig,
    CompressEmbeddingsConfig,
    EncodingTextConfig,
    DateExtractionConfig,
    NumericalFeaturesConfig,
    FlagFeatureConfig,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def generate_embeddings(texts: List[str], embeddings_config: EmbeddingsConfig) -> np.ndarray:
    """
    Generate the embeddings from the input texts through the method
    specified in embeddings_config.method.

    Args:
        texts (str): Input text
        embeddings_config (EmbeddingsConfig): Object including embedding configurations

    Returns:
        sentence_embeddings (numpy.ndarray): Embedded texts (n_samples, embeddings_size)
    """
    # Retrieve embeddings' method
    method = embeddings_config.method

    # Initialise result
    sentence_embeddings = None

    logging.info(f"\t🧠 Generate embeddings with method: {method}")

    # Switch based on the embeddings' method
    match method:
        case "SentenceTransformer":
            # Instance model
            model = SentenceTransformer(embeddings_config.embedding_model_config.model_name)

            # generate embeddings
            sentence_embeddings = model.encode(
                texts, convert_to_numpy=embeddings_config.embedding_model_config.numpy_tensor
            )
        case _:
            logging.error(f"\t🚨 Unknown embedding method: {method}")
            raise ValueError("Invalid embedding method")

    return sentence_embeddings


def compress_embeddings(
    input_embeddings: np.ndarray, compress_embeddings_config: CompressEmbeddingsConfig
) -> np.ndarray:
    """
    Compress the input embeddings with the corresponding selected method in
    `compress_embeddings_config.method`.

    Args:
        input_embeddings (numpy.ndarray): Input embeddings (n_samples, embeddings_size)
        compress_embeddings_config (CompressEmbeddingsConfig): Compress algorithm configs

    Returns:
        compressed_embeddings (numpy.ndarray): Output embeddings compressed (n_samples, n_components)
    """
    # Retrieve compress method
    method = compress_embeddings_config.method

    # Initialise result
    compressed_embeddings = None

    logging.info(f"\t🧠 Compress embeddings with method: {method}")

    # Switch based on the compress method
    match method:
        case "PCA":
            # Instance model
            model = PCA(n_components=compress_embeddings_config.compress_model_config.n_components)

            # Compress embeddings
            compressed_embeddings = model.fit_transform(input_embeddings)

        case _:
            logging.error(f"\t🚨 Unknown compression method: {method}")
            raise ValueError("Invalid compression method")

    return compressed_embeddings


def encode_text(
    texts: List[str],
    config: EncodingTextConfig,
) -> np.ndarray:
    """
    Encode an input text through embeddings and compress their dimensionality.

    Args:
        texts (List[str]): Input texts
        config (EncodingTextConfig): Object including embedding configurations

    Returns:
        compressed_embeddings (numpy.ndarray): Output embeddings compressed (n_samples, n_components)
    """
    # Generate embeddings
    embeddings = generate_embeddings(texts, config.embeddings_config)

    # Compress embeddings
    compressed_embeddings = compress_embeddings(embeddings, config.compress_embeddings_config)

    return compressed_embeddings


def extract_date_information(data: pd.DataFrame, config: DateExtractionConfig) -> pd.DataFrame:
    """
    Extract date information from a column included in the ``config.column_name`` like the year, the month, etc.

    Args:
        data (pd.DataFrame): Input data
        config (DateExtractionConfig): Configuration including the column_name and date information to extract

    Returns:
        (pd.DataFrame): Output data with additional columns
    """
    # Retrieve column name
    column_name = config.column_name

    logging.info(f"\t🗓️ Extract date information from column: {column_name}")

    # Convert column to datetime
    data[column_name] = pd.to_datetime(data[column_name])

    # Extract date information
    if config.extract_year:
        data[f"{column_name}_year"] = data[column_name].dt.year
    if config.extract_month:
        data[f"{column_name}_month"] = data[column_name].dt.month

    return data


def standardise_features(data: pd.DataFrame, config: NumericalFeaturesConfig) -> pd.DataFrame:
    """
    Apply the specific standardisation method in ``config.standardisation`` on the data column ``config.column_name``

    Args:
        data (pd.DataFrame): Input data
        config (NumericalFeaturesConfig): Object including transformation configurations

    Returns:
        (pd.DataFrame): Output data with additional columns
    """
    # Retrieve configurations
    column_name = config.column_name
    standardisation = config.standardisation

    logging.info(f"\t🛠️ Standardise feature {column_name} with method: {standardisation}")

    # Switch based on the standardisation method
    match standardisation:
        case "min_max_scaler":
            # Instance the MinMaxScaler
            min_max_scaler = MinMaxScaler()

            # Apply transformation
            data.loc[:, f"{column_name}_standardised"] = min_max_scaler.fit_transform(
                data[[column_name]]
            )

        case _:
            logging.error(f"\t🚨 Unknown standardisation method: {standardisation}")
            raise ValueError("Invalid standardisation method")

    return data


def drop_outliers(data: pd.DataFrame, config: NumericalFeaturesConfig) -> pd.DataFrame:
    """
    Apply the specific drop outliers method in ``config.drop_outliers`` on the data column ``config.column_name``

    Args:
        data (pd.DataFrame): Input data
        config (NumericalFeaturesConfig): Object including transformation configurations

    Returns:
        (pd.DataFrame): Output data with additional columns
    """
    # Retrieve configurations
    column_name = config.column_name
    drop_outliers_method = config.drop_outliers.method

    logging.info(
        f"\t🪂️ Drop outliers from feature {column_name} with method: {drop_outliers_method}"
    )

    match drop_outliers_method:
        case "z_score":
            # Compute z-score
            data.loc[:, f"{column_name}_{drop_outliers_method}"] = zscore(data[column_name])

            # Drop outliers
            data = data[
                data[f"{column_name}_{drop_outliers_method}"].abs() <= config.drop_outliers.n_std
            ]

        case "iqr":
            # Compute Q1 and Q3
            q1 = data[column_name].quantile(0.25)
            q3 = data[column_name].quantile(0.75)
            iqr = q3 - q1

            # Define the bounds
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            # Filter outliers
            data = data[(data[column_name] >= lower_bound) & (data[column_name] <= upper_bound)]

        case _:
            logging.error(f"\t🚨 Unknown drop outliers method: {drop_outliers_method}")
            raise ValueError("Invalid drop outliers method")

    return data


def manage_nan_values(data: pd.DataFrame, config: NumericalFeaturesConfig) -> pd.DataFrame:
    """
    Apply the specific drop outliers method in ``config.nan_values`` on the data column ``config.column_name``

    Args:
        data (pd.DataFrame): Input data
        config (NumericalFeaturesConfig): Object including transformation configurations

    Returns:
        (pd.DataFrame): Output data with applied transformation
    """
    # Retrieve configurations
    column_name = config.column_name
    nan_values_method = config.nan_values

    logging.info(
        f"\t🪹 Manage NaN value from feature {column_name} with method: {nan_values_method}"
    )

    match nan_values_method:
        case "drop_nan":
            # Drop NaN values
            data = data.dropna(subset=[column_name])

        case _:
            logging.error(f"\t🚨 Unknown nan values method: {nan_values_method}")
            raise ValueError("Invalid nan values method")

    logging.debug("manage_nan_values - End")

    return data


def prepare_numerical_features(data: pd.DataFrame, config: NumericalFeaturesConfig) -> pd.DataFrame:
    """
    Apply a set of transformation to the selected column in ``config.column_name``.

    Args:
        data (pd.DataFrame): Input data
        config (NumericalFeaturesConfig): Set of transformation configurations

    Returns:
        (pd.DataFrame): Prepared data
    """
    # Apply drop outliers
    data = drop_outliers(data, config)

    # Apply nan values
    data = manage_nan_values(data, config)

    # Apply standardisation
    data = standardise_features(data, config)

    return data


def create_flag_feature(data: pd.DataFrame, config: FlagFeatureConfig) -> pd.DataFrame:
    """
    Create a flag feature from the column in ``config.column_name``.

    Args:
        data (pd.DataFrame): Input data
        config (FlagFeatureConfig): Information on the column to use

    Returns:
        (pd.DataFrame): Prepared data
    """

    logging.info(f"\t🏳 Creating flag feature from column {config.column_name}")

    # Create a flag feature where the column has a value
    data.loc[:, config.output_column_name] = data.loc[:, config.column_name].notna()

    return data
