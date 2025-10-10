# -*- coding: utf-8 -*-
"""
    RAISE - RAI Synthetic Data Generator

    @author: Mikel Hernández Jiménez - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @author: Mikel Catalina Olazaguirre - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @version: 0.1
"""

# ============================================
# IMPORTS
# ============================================


# Stdlib imports
from dataclasses import dataclass

# Third-party app imports
import pandas as pd
from sdv.single_table import TVAESynthesizer
from sdv.metadata import SingleTableMetadata

# Imports from your apps
from raise_synthetic_data_generator.sdg_models.AbstractModel import (
    SDGModelParams,
    AbstractModel,
)

# ============================================
# GLOBAL CONSTANTS
# ============================================


# ============================================
# CLASSES
# ============================================


@dataclass
class TVAEModelParams(SDGModelParams):
    enforce_rounding: bool = True
    embedding_dim: int = 128
    batch_size: int = 500
    enforce_min_max_values: bool = True
    epochs: int = 300
    compress_dims: tuple[int, ...] = (128, 128)
    loss_factor: int = 2
    l2scale: float = 1e-5


class TVAEModel(AbstractModel):
    def __init__(self, model_params: TVAEModelParams):
        super().__init__(
            model_params=model_params,
            model_name="tvae",
            package_name="sdv",
            references=[
                "https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/tvaesynthesizer",
                "http://web2.cs.columbia.edu/~blei/fogm/2018F/materials/KingmaWelling2013.pdf",
            ],
        )

    def _initialize_model_internal(self, input_data: pd.DataFrame):
        """
        Initialize the TVAE model instance with the provided input data.

        Args:
            input_data (pd.DataFrame): Training data for the model.

        Returns:
            None

        Raises:
            TypeError: If input_data is not a pandas DataFrame.
            ValueError: If input_data is missing required columns.
        """
        if not isinstance(input_data, pd.DataFrame):
            raise TypeError("input_data must be a pandas DataFrame.")

        metadata = SingleTableMetadata()
        metadata.detect_from_dataframe(input_data)

        self.model = TVAESynthesizer(
            metadata=metadata,
            enforce_rounding=self.model_params.enforce_rounding,
            embedding_dim=self.model_params.embedding_dim,
            batch_size=self.model_params.batch_size,
            enforce_min_max_values=self.model_params.enforce_min_max_values,
            epochs=self.model_params.epochs,
            compress_dims=self.model_params.compress_dims,
            loss_factor=self.model_params.loss_factor,
            l2scale=self.model_params.l2scale,
        )

    def _train_model_internal(self, input_data: pd.DataFrame):
        """
        Train the TVAE model on the provided input data.

        Args:
            input_data (pd.DataFrame): Training data for the model.

        Returns:
            None
        """
        self.model.fit(input_data)

    def _generate_data_internal(self, n_samples: int):
        """
        Generate synthetic data samples using the trained TVAE model.

        Args:
            n_samples (int): Number of synthetic samples to generate.

        Returns:
            pd.DataFrame: DataFrame containing the generated synthetic samples.

        Raises:
            RuntimeError: If the model has not been initialized.
        """
        if self.model is None:
            raise RuntimeError(
                "Model is not initialized. Call _initialize_model_internal first."
            )
        return self.model.sample(num_rows=n_samples)

    def _save_model_internal(self, filename: str = None):
        """
        Save the trained TVAE model to disk.

        Args:
            filename (str, optional): The filename to save the model.

        Returns:
            str: The filename where the model was saved.

        Raises:
            RuntimeError: If the model has not been initialized.
        """
        if self.model is None:
            raise RuntimeError(
                "Model is not initialized. Call _initialize_model_internal first."
            )
        if filename is None:
            filename = f"{self.model_name}.pkl"
        self.model.save(filename)
        return filename


# ============================================
# PUBLIC METHODS
# ============================================


# ============================================
# PRIVATE METHODS
# ============================================


# ============================================
# MAIN BLOCK
# ============================================
