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
from sdv.single_table import GaussianCopulaSynthesizer
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
class GaussianCopulaModelParams(SDGModelParams):
    enforce_rounding: bool = True
    enforce_min_max_values: bool = True


class GaussianCopulaModel(AbstractModel):
    def __init__(
        self, model_params: GaussianCopulaModelParams, save_filename: str = None
    ) -> None:
        super().__init__(
            model_params=model_params,
            model_name="gaussian_copula",
            package_name="sdv",
            references=[
                "https://docs.sdv.dev/sdv/single-table-data/modeling/synthesizers/gaussiancopulasynthesizer",
                "https://arxiv.org/abs/2101.00598",
            ],
        )
        self.save_filename = save_filename or f"{self.model_name}.pkl"

    def _initialize_model_internal(self, input_data: pd.DataFrame) -> None:
        if not isinstance(input_data, pd.DataFrame) or input_data.empty:
            raise ValueError("`input_data` must be a non-empty pandas DataFrame.")
        try:
            metadata = SingleTableMetadata()
            metadata.detect_from_dataframe(input_data)
            self.model = GaussianCopulaSynthesizer(
                metadata=metadata,
                enforce_rounding=self.model_params.enforce_rounding,
                enforce_min_max_values=self.model_params.enforce_min_max_values,
            )
        except Exception as e:
            # Log and handle the exception as needed
            print(f"Error initializing GaussianCopulaSynthesizer: {e}")
            raise

    def _train_model_internal(self, input_data: pd.DataFrame) -> None:
        if not isinstance(input_data, pd.DataFrame) or input_data.empty:
            raise ValueError("`input_data` must be a non-empty pandas DataFrame.")
        try:
            self.model.fit(input_data)
        except Exception as e:
            print(f"Error fitting the model: {e}")
            raise

    def _generate_data_internal(self, n_samples: int) -> pd.DataFrame:
        return self.model.sample(num_rows=n_samples)

    def _save_model_internal(self) -> str:
        try:
            self.model.save(self.save_filename)
            return self.save_filename
        except Exception as e:
            print(f"Error saving the model: {e}")
            raise


# ============================================
# PUBLIC METHODS
# ============================================


# ============================================
# PRIVATE METHODS
# ============================================


# ============================================
# MAIN BLOCK
# ============================================
