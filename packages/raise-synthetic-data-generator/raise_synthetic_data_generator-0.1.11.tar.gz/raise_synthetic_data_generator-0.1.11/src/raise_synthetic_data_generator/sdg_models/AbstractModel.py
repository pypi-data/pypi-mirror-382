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
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import pkg_resources
from datetime import datetime

# Third-party app imports
import pandas as pd

# Imports from your apps
from raise_synthetic_data_generator.custom_exceptions import SDGError

# ============================================
# GLOBAL CONSTANTS
# ============================================


# ============================================
# CLASSES
# ============================================


@dataclass
class SDGModelParams:
    # Inherit and include required params. These methods permit accessing members as dictionary items.

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, item_value):
        return setattr(self, key, item_value)


class AbstractModel(ABC):
    def __init__(
        self,
        model_params: SDGModelParams,
        model_name: str,
        package_name: str,
        references: list,
    ):
        self.model_params = model_params
        self.model_name = model_name
        self.package_name = package_name

        if not package_name:
            raise SDGError(
                message="`package_name` must be provided for version retrieval."
            )
        try:
            self.package_version = pkg_resources.get_distribution(package_name).version
        except Exception as exc:
            raise SDGError(
                message=f"Could not retrieve version for package `{package_name}`: {exc}"
            )

        self.references = references

    @property
    def model_params(self):
        return self.__params

    @model_params.setter
    def model_params(self, parameter):
        self.__params = parameter

    def _wrap_with_sdg_error(self, method, error_action, *args, **kwargs):
        try:
            return method(*args, **kwargs)
        except Exception as exception:
            raise SDGError(
                message=f"Error {error_action} {self.model_name} model. Traceback: {str(exception)}"
            )

    def initialize_model(self, input_data: pd.DataFrame):
        self._wrap_with_sdg_error(
            self._initialize_model_internal, "initializing", input_data=input_data
        )

    def train_model(self, input_data: pd.DataFrame):
        self._wrap_with_sdg_error(
            self._train_model_internal, "training", input_data=input_data
        )

    def generate_data(self, n_samples: int):
        if not isinstance(n_samples, int) or n_samples <= 0:
            raise SDGError(
                message=f"`n_samples` must be a positive integer. Got {n_samples!r}."
            )
        try:
            synthetic_data = self._generate_data_internal(n_samples=n_samples)
            if synthetic_data.shape[0] > 1:
                return synthetic_data
            else:
                raise SDGError(
                    message=f"Error generating {n_samples} samples with {self.model_name} model"
                )
        except Exception as exception:
            raise SDGError(
                message=f"""Error generating {n_samples} samples with {self.model_name} model.
                    Traceback: {str(exception)}"""
            )

    def generate_model_information_text(self):
        date = datetime.now().strftime("%Y-%m-%d")
        info_text = "The provided synthetic data was generated using the SDG model described below:\n"
        info_text += f"- Synthetic data generation date: {date}\n"
        info_text += f"- Model name: {self.model_name}\n"
        info_text += f"- Package: {self.package_name}, version {self.package_version}\n"
        info_text += "- Training parameters:\n"

        params_dict = asdict(self.model_params)
        for param, param_value in params_dict.items():
            info_text += f"   - {param}: {param_value}\n"

        info_text += "\nReferences:\n"
        for reference in self.references:
            info_text += f"- {reference}\n"
        return info_text

    @abstractmethod
    def _initialize_model_internal(self, input_data: pd.DataFrame):
        raise NotImplementedError("This method must be implemented by any child class")

    @abstractmethod
    def _train_model_internal(self, input_data: pd.DataFrame):
        raise NotImplementedError("This method must be implemented by any child class")

    @abstractmethod
    def _generate_data_internal(self, n_samples: int):
        raise NotImplementedError("This method must be implemented by any child class")

    @abstractmethod
    def _save_model_internal(self):
        raise NotImplementedError("This method must be implemented by any child class")


# ============================================
# PUBLIC METHODS
# ============================================


# ============================================
# PRIVATE METHODS
# ============================================


# ============================================
# MAIN BLOCK
# ============================================
