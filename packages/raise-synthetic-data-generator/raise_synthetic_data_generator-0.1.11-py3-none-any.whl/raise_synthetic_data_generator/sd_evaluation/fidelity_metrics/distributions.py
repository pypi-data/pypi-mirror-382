# -*- coding: utf-8 -*-
"""
    RAISE - RAI Synthetic Data Generator

    @author: Mikel Hernández Jiménez - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @author: Mikel Catalina Olazaguirre - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @version: 0.1
"""
# Stdlib imports

# Third-party app imports
import pandas as pd
import numpy as np
from scipy.linalg import norm

# Imports from your apps
from raise_synthetic_data_generator.sd_evaluation.fidelity_metrics.visualizations import (
    hellinger_distance_per_variable,
)
import raise_synthetic_data_generator.sd_evaluation.evaluation_report.__global_variables__ as g


def __hellinger_distance(p_array: np.array, q_array: np.array) -> float:
    """
    function to compute the hellinger distance between two probability distributions
    https://en.wikipedia.org/wiki/Hellinger_distance

    Args:
        p_array: First probability distribution
        q_array: Second probability distribution

    Returns: A float value [0..1]. 0 distance implies same distribution and 1 completely different.

    """
    # interpolate the probability distributions to have the same length
    min_len = min(len(p_array), len(q_array))
    p_interp = np.interp(
        np.linspace(0, len(p_array) - 1, min_len), np.arange(len(p_array)), p_array
    )
    q_interp = np.interp(
        np.linspace(0, len(q_array) - 1, min_len), np.arange(len(q_array)), q_array
    )
    # compute and return hellinger distance
    h_dist = norm(np.sqrt(p_interp) - np.sqrt(q_interp)) / np.sqrt(2)
    return h_dist


def __compute_probability_distribution(data_content: pd.Series) -> np.ndarray:
    """
    This method computes the probability distribution for a feature. It must be a numeric column.
    Args:
        data_content: Feature column with samples taken from a pandas DataFrame

    Returns: The increasing sorted probabilities for all values

    """
    value_counts = data_content.value_counts(normalize=True, sort=False)
    return value_counts.sort_index().values


def hellinger_distances(
    real_data: pd.DataFrame, synthetic_data: pd.DataFrame, figures_path: str
) -> (dict, float):
    """
    Generates a dictionary containing the hellinger distance values for all features in a pandas
    DataFrame table

    Args:
        real_data: pandas Dataframe containing real sample set
        synthetic_data: pandas Dataframe containing the synthetic sample set

    Returns: A dictionary where the key is the column name and the value contains the Helling distance

    """
    #
    hellinger_d = dict()

    # iterate over all dataset columns to compute the hellinger distance for each variable
    for column in real_data.columns.tolist():
        p_array = __compute_probability_distribution(real_data[column])
        q_array = __compute_probability_distribution(synthetic_data[column])
        hellinger_d[column] = __hellinger_distance(p_array, q_array)

    mean_hellinger = float(np.array(list(hellinger_d.values())).mean())
    hellinger_distance_per_variable(
        hellinger_distances=hellinger_d, mean_hellinger=mean_hellinger
    ).savefig(fname=f"{figures_path}/{g.hellinger_png_path}", dpi=300, format="png")

    # return the Hellinger distances
    return hellinger_d, mean_hellinger
