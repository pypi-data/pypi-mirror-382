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
from sdv.single_table import CTGANSynthesizer
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
class CTGANModelParams(SDGModelParams):
    """
    Parameters for configuring the CTGAN model.

    Attributes:
        enforce_rounding (bool): If True, round numerical outputs to integers where appropriate. Default is True.
        embedding_dim (int): Size of the random sample passed to the generator. Default is 128.
        batch_size (int): Number of samples per batch during training. Default is 500.
        enforce_min_max_values (bool): Whether to enforce min/max values in output. Default is True.
        epochs (int): Number of training epochs. Default is 300.
        verbose (bool): Verbosity level; True will print training progress. Default is True.
        generator_dim (tuple): Layers for generator network. Default is (256, 256).
        generator_decay (float): Weight decay for generator optimizer. Default is 1e-6.
        discriminator_dim (tuple): Layers for discriminator network. Default is (256, 256).
        discriminator_decay (float): Weight decay for discriminator optimizer. Default is 1e-6.
        generator_lr (float): Learning rate for generator. Default is 2e-4.
        discriminator_lr (float): Learning rate for discriminator. Default is 2e-4.
    """

    enforce_rounding: bool = True
    embedding_dim: int = 128
    batch_size: int = 500
    enforce_min_max_values: bool = True
    epochs: int = 300
    verbose: bool = True
    generator_dim: tuple = (256, 256)
    generator_decay: float = 1e-6
    discriminator_dim: tuple = (256, 256)
    discriminator_decay: float = 1e-6
    generator_lr: float = 2e-4
    discriminator_lr: float = 2e-4


class CTGANModel(AbstractModel):
    def __init__(self, model_params: CTGANModelParams):
        super().__init__(
            model_params=model_params,
            model_name="ctgan",
            package_name="sdv",
            references=[
                "https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/ctgansynthesizer",
                "https://arxiv.org/abs/1907.00503",
            ],
        )

    def _initialize_model_internal(self, input_data: pd.DataFrame):
        if not isinstance(input_data, pd.DataFrame) or input_data.empty:
            raise ValueError("`input_data` must be a non-empty pandas DataFrame")
        metadata = SingleTableMetadata()
        metadata.detect_from_dataframe(input_data)

        self.model = CTGANSynthesizer(
            metadata=metadata,
            enforce_rounding=self.model_params.enforce_rounding,
            embedding_dim=self.model_params.embedding_dim,
            batch_size=self.model_params.batch_size,
            enforce_min_max_values=self.model_params.enforce_min_max_values,
            epochs=self.model_params.epochs,
            verbose=self.model_params.verbose,
            generator_dim=self.model_params.generator_dim,
            generator_decay=self.model_params.generator_decay,
            discriminator_dim=self.model_params.discriminator_dim,
            discriminator_decay=self.model_params.discriminator_decay,
            generator_lr=self.model_params.generator_lr,
            discriminator_lr=self.model_params.discriminator_lr,
        )

    def _train_model_internal(self, input_data: pd.DataFrame):
        if not isinstance(input_data, pd.DataFrame) or input_data.empty:
            raise ValueError("`input_data` must be a non-empty pandas DataFrame")
        self.model.fit(input_data)

    def _generate_data_internal(self, n_samples: int):
        return self.model.sample(num_rows=n_samples)

    def _save_model_internal(self):
        try:
            filename = f"{self.model_name}.pkl"
            self.model.save(filename)
        except (IOError, OSError, Exception) as exception:
            # Consider using a logger in production code
            print(f"Error saving model to {filename}: {exception}")
            raise exception
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
