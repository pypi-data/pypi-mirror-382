# -*- coding: utf-8 -*-
"""
    RAISE - RAI Synthetic Data Generator

    @author: Mikel Hernández Jiménez - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @version: 0.1
"""
# Stdlib imports

# Third-party app imports

# Imports from your apps


class SDGError(Exception):
    """Exception raised when there is a problem generating synthetic data from a trained model."""

    def __init__(
        self, message="There has been a problem when generating synthetic data"
    ):
        super().__init__(message)


class SDGModelSelectionError(Exception):
    """Exception raised when there is a problem selecting the SDG model."""

    def __init__(
        self, message="There has been a problem when selecting the proper SDG model"
    ):
        super().__init__(message)
