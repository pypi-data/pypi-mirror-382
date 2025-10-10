# -*- coding: utf-8 -*-
"""
    RAISE - RAI Synthetic Data Generator

    @author: Mikel Hernández Jiménez - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @author: Mikel Catalina Olazaguirre - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @version: 0.1
"""
# Stdlib imports

# Third-party app imports
from scipy.stats import mannwhitneyu
from scipy.stats import chisquare
import pandas as pd

# Imports from your apps


def mann_whitney(
    real_data: pd.DataFrame,
    synthetic_data: pd.DataFrame,
    significance_level: float = 0.1,
) -> (dict, float):
    """

    Performs the Mann Whitney test. Non-parametric statistical test that determines if there is a difference in the
    dependent variable for two independent samples. This is a univariate test performed per each column in the
    dataset independently. Used for numerical variables, not for binary or categorical.

    Higher (near to 1) the best. [0..1]

    Args:
        real_data: pandas Dataframe containing the original dataset
        synthetic_data: pandas Dataframe containing the synthetic dataset
        significance_level: Confidence level to consider acceptable the test (p_value threshold)

    Returns: The tests results as a tuple: {column_name: p_value}, proportion of variables with p_value >
    significance_level

    """
    # generate dictionaries to save the p_values
    p_values = dict()

    # iterate over all dataset columns to perform the test for each variable
    for column in real_data.columns.tolist():
        real_vals = real_data[column]
        synthetic_vals = synthetic_data[column]
        try:
            _, p_values[column] = mannwhitneyu(real_vals, synthetic_vals)
        except Exception as e:
            raise ValueError from e

    # compute the proportion of variables that does not reject the null hypothesis
    n_cols_not_reject = sum(
        1 for p_value in p_values.values() if p_value > significance_level
    )
    variables_proportion = float(n_cols_not_reject) / len(p_values)

    return p_values, variables_proportion


def chi_square(
    real_data: pd.DataFrame,
    synthetic_data: pd.DataFrame,
    significance_level: float = 0.1,
):
    """
    Chi square test. Statistical test to determine if there is a statistical relationship between two
    categorical variables (or binary). This is a univariate test performed per each column in the
    dataset independently.

    Higher (near to 1) the best. [0..1]

    Args:
        real_data: pandas Dataframe containing the original dataset
        synthetic_data: pandas Dataframe containing the synthetic dataset
        significance_level: Confidence level to consider acceptable the test (p_value threshold)

    Returns:  The tests results as a tuple: {column_name: p_value}, proportion of variables with p_value >
    significance_level

    """
    # generate dictionaries to save the p_values
    p_values = dict()

    # iterate over all dataset columns to perform the test for each variable
    for column in real_data.columns.tolist():
        real_vals = real_data[column].value_counts()
        synthetic_vals = synthetic_data[column].value_counts()

        # Ensure the same categories are present in both datasets
        all_categories = real_vals.index.union(synthetic_vals.index)
        real_vals = real_vals.reindex(all_categories, fill_value=0)
        synthetic_vals = synthetic_vals.reindex(all_categories, fill_value=0)

        # Normalize frequencies
        real_vals_sum = real_vals.sum()
        synthetic_vals_sum = synthetic_vals.sum()
        real_vals = real_vals / real_vals_sum
        synthetic_vals = synthetic_vals / synthetic_vals_sum

        # Performs the test
        _, p_values[column] = chisquare(f_obs=synthetic_vals, f_exp=real_vals)

    # compute the proportion of variables that does not reject the null hypothesis
    n_cols_not_reject = sum(
        1 for p_value in p_values.values() if p_value > significance_level
    )
    variables_proportion = float(n_cols_not_reject) / len(p_values)

    # return the tests results
    return p_values, variables_proportion
