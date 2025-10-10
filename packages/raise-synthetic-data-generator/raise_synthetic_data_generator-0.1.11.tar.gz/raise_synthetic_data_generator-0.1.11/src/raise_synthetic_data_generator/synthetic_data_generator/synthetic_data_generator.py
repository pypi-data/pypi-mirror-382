# -*- coding: utf-8 -*-
"""
    RAISE Synthetic Data Generator

    @author: Mikel Hernández Jiménez - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @author: Mikel Catalina Olazaguirre - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @version: 0.1
"""

# ============================================
# IMPORTS
# ============================================

# Stdlib imports

# Third-party app imports
import pandas as pd
from pathlib import Path

# Imports from your apps
from raise_synthetic_data_generator.sdg_models.CTGANModel import (
    CTGANModel,
    CTGANModelParams,
)
from raise_synthetic_data_generator.sdg_models.TVAEModel import (
    TVAEModel,
    TVAEModelParams,
)
from raise_synthetic_data_generator.sdg_models.GaussianCopulaModel import (
    GaussianCopulaModel,
    GaussianCopulaModelParams,
)


# ============================================
# GLOBAL CONSTANTS
# ============================================

MAX_SIZE = 1 * 1024 * 1024

MODELS = {
    "CTGAN": lambda: CTGANModel(model_params=CTGANModelParams()),
    "TVAE": lambda: TVAEModel(model_params=TVAEModelParams()),
    "Copulas": lambda: GaussianCopulaModel(model_params=GaussianCopulaModelParams()),
}
MODELS_CUSTOM = {
    "CTGAN":  CTGANModel,
    "TVAE":  TVAEModel,
    "Copulas":  GaussianCopulaModel,
}


# ============================================
# CLASSES
# ============================================


class SyntheticDataGenerator:
    def __init__(self, dataset: pd.DataFrame, sdg_model: str, parameters: dict = None):
        super().__init__()
        if sdg_model not in MODELS:
            raise ValueError(
                f"`sdg_model` must be one of {list(MODELS.keys())}, got '{sdg_model}'"
            )
        self.original_data = dataset
        if parameters is None: # Use default parameters
            self.sdg_model = MODELS[sdg_model]()
        else: # Use tunned parameters
            params_class = {
                "CTGAN": CTGANModelParams,
                "TVAE": TVAEModelParams,
                "Copulas": GaussianCopulaModelParams,
                }[sdg_model]
            params_obj = params_class(**parameters)
            self.sdg_model = MODELS_CUSTOM[sdg_model](model_params=params_obj)


    def generate_synthetic_data(self, n_samples: int) -> pd.DataFrame:
        self.sdg_model.initialize_model(input_data=self.original_data)
        self.sdg_model.train_model(input_data=self.original_data)
        if n_samples is not None:
            n_samples = self.original_data.shape[0]
        return self.sdg_model.generate_data(n_samples=n_samples)

    def get_model_info(self):
        return self.sdg_model.generate_model_information_text()

    def store_model_info(self, output_folder: Path):
        model_info_text = self.sdg_model.generate_model_information_text()
        filepath = output_folder / "info.txt"
        try:
            with filepath.open("w", encoding="utf-8") as file:
                file.write(model_info_text)
        except IOError as e:
            print(f"Failed to write model info to {filepath}: {e}")


# ============================================
# PUBLIC METHODS
# ============================================


# ============================================
# PRIVATE METHODS
# ============================================


# ============================================
# MAIN BLOCK
# ============================================
