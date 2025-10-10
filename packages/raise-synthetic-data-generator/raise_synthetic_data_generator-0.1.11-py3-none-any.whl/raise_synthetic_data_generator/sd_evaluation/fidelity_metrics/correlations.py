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
import phik  # noqa: F401
from matplotlib import pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

# Imports from your apps
import raise_synthetic_data_generator.sd_evaluation.evaluation_report.__global_variables__ as g


# function to compute the pcd
def __pairwise_correlation_difference(
    real_data: np.ndarray, synthetic_data: np.ndarray
) -> float:
    """
    Metrics to compare the difference between the pairwise correlation matrices of real and synthetic data.
    For Numerical, Binary and Categorical. Multivariate evaluation

    Lower (near 0) is the best. Range [0..1]

    Args:
        real_data: numpy ndarray containing real sample set
        synthetic_data: numpy ndarray containing synthetic sample set

    Returns: Returns the correlation difference

    """
    cors_difference = np.abs(synthetic_data - real_data)
    pcd = np.mean(cors_difference)
    return pcd


def __correlation_matrix(data_content: pd.DataFrame) -> np.ndarray:
    """
    Compute the correlation matrices using external package phik
    Args:
        data_content: pandas Dataframe with dataset

    Returns: Compressed numpy array. Removing self correlation diagonal.

    """
    # compute the phik correlation matrix
    cors = data_content.phik_matrix()
    # FIXME: for mhernanded Check if this redundancy removal is correct delete redundancy of the correlation matrix
    cors = cors.iloc[1:, 0:-1]
    # return the correlation matrix
    return cors.values


def __correlation_comparison_figure(
    synthetic_cors: pd.DataFrame,
    correlation_difference: float,
    columns: list,
):
    """
    Compute and plot the correlation matrix for synthetic data only.

    Args:
        synthetic_cors: pandas DataFrame with synthetic dataset correlations.
        correlation_difference: Pairwise Correlation Difference value.
        columns: List of column names.

    Returns: Matplotlib figure showing the correlation matrix of the synthetic data.
    """
    # Define figure size dynamically based on the number of columns
    height = max(0.3 * len(synthetic_cors), 4)
    fig, ax = plt.subplots(figsize=(height * 2, height))

    # Create mask to hide upper triangle (optional, keeps lower triangle view)
    synthetic_cors_mask = np.triu(
        np.ones_like(synthetic_cors, dtype=bool)
    ) - np.identity(len(synthetic_cors))

    # Define tu colormap personalizado con tu color
    custom_cmap = LinearSegmentedColormap.from_list(
        "custom_blues", ["#ffffff", "#028692"]
    )
    # Plot synthetic data correlation heatmap
    sns.heatmap(
        synthetic_cors,
        linewidths=0.3,
        yticklabels=columns[1:],
        xticklabels=columns[:-1],
        mask=synthetic_cors_mask,
        ax=ax,
        cbar=True,
        annot=False,
        vmin=0,
        vmax=1,
        cmap=custom_cmap,
    )
    ax.set_title("Synthetic Data Correlations")

    # Adjust layout and add title
    fig.suptitle(f"PCD: {round(correlation_difference, 4)}")
    fig.tight_layout()

    return fig


def pairwise_correlation_difference(
    real_data: pd.DataFrame,
    synthetic_data: pd.DataFrame,
    figures_path: str,
) -> float:
    """
    Compute the absolute difference of the correlation matrices with the phi_k constant.
    Compute the PCD between both correlation matrices.

    Note: diagonal with self correlations in the correlation matrix are removed before any other computation
    Lower (near 0) is the best. Range [0..1]

    Args:
        real_data: numpy ndarray containing real sample set
        synthetic_data: numpy ndarray containing synthetic sample set

    Returns: Returns the correlation difference

    """
    # compute correlations of real data
    real_cors = __correlation_matrix(data_content=real_data)
    # compute and plot correlations of synthetic data
    synthetic_cors = __correlation_matrix(data_content=synthetic_data)

    # compute the pairwise correlation difference
    pcd = __pairwise_correlation_difference(real_cors, synthetic_cors)

    # create the correlations comparison figure
    correlations_fig = __correlation_comparison_figure(
        synthetic_cors=synthetic_cors,
        correlation_difference=pcd,
        columns=real_data.columns.tolist(),
    )

    correlations_fig.savefig(
        fname=f"{figures_path}/{g.cors_png_path}", dpi=300, format="png"
    )
    return pcd, correlations_fig
