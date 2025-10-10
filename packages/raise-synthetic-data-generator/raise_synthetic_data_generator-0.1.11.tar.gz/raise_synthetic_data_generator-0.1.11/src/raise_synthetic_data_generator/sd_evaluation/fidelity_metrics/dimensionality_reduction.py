# -*- coding: utf-8 -*-
"""
    RAISE - RAI Synthetic Data Generator

    @author: Mikel Hernández Jiménez - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @author: Mikel Catalina Olazaguirre - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @version: 0.1
"""
# Stdlib imports

# Third-party app imports
import matplotlib.pyplot as plt
import numpy as np
from openTSNE import TSNE
import pandas as pd
from sklearn.manifold import Isomap
from sklearn.metrics import r2_score
from sklearn.preprocessing import OneHotEncoder
from typing import List
from umap import UMAP

# Imports from your apps
import raise_synthetic_data_generator.sd_evaluation.evaluation_report.__global_variables__ as g
from raise_synthetic_data_generator.sd_evaluation.fidelity_metrics.visualizations import (
    tsne_isomap_umap_visualization_image,
)


def __euclidean_distance(x_values, y_values):
    return np.sqrt(np.sum((x_values - y_values) ** 2))


def __calculate_denominator(X_values, Y_values, Z_values):
    Z_distances_X = np.sum(
        np.array(
            [
                [__euclidean_distance(x_values, z_values) for x_values in X_values]
                for z_values in Z_values
            ]
        ),
        axis=1,
    )
    den_X = np.sum(Z_distances_X)

    Z_distances_Y = np.sum(
        np.array(
            [
                [__euclidean_distance(y_values, z_values) for y_values in Y_values]
                for z_values in Z_values
            ]
        ),
        axis=1,
    )
    den_Y = np.sum(Z_distances_Y)
    print(Z_distances_X.shape)

    return den_X, den_Y, Z_distances_X, Z_distances_Y


def __calculate_DD(X_values, Y_values, Z_values):
    den_X, den_Y, Z_distances_X, Z_distances_Y = __calculate_denominator(
        X_values, Y_values, Z_values
    )
    DF_n = 1 - (Z_distances_X / den_X)
    DG_m = 1 - (Z_distances_Y / den_Y)
    return DF_n, DG_m


def __encode_categorical(df: pd.DataFrame, column: str) -> pd.DataFrame:
    count = df[column].value_counts().sort_values(ascending=False)
    cum_perc = count.cumsum() / count.sum()
    # Getting intervals
    intervals = []
    for cum_val in range(len(cum_perc)):
        if cum_val == 0:
            intervals.append((0, cum_perc.iloc[cum_val]))
        else:
            intervals.append((cum_perc.iloc[cum_val - 1], cum_perc.iloc[cum_val]))
    temp_categorical = []
    cat_var = df[column]
    for row in range(len(df)):
        # Find the interval that corresponds to the category
        idx = np.where(cat_var[row] == np.array(count.index))[0][0]
        a_interval, b_interval = intervals[idx]
        # Choose a value between a and b by sampling from a Truncated Gaussian distribution,
        # with miu at the center and delta = (b-a)/6
        miu = (a_interval + b_interval) / 2
        delta = (b_interval - a_interval) / 6
        temp_categorical.append(np.random.normal(miu, delta, 1)[0])
    return temp_categorical


def ddplot(
    synthetic_data: pd.DataFrame,
    real_data: pd.DataFrame,
    categorical_columns,
    figures_path: str,
) -> (np.ndarray, np.ndarray, float):
    """
    Args:
        real_data: pandas Dataframe containing real sample set
        synthetic_data: pandas Dataframe containing synthetic sample set
        categorical_columns: list of strings containing the names of categorical (including binary) columns

    Returns: a tuple with three values:
        1. numpy ndarray containing depth measurments of synthetic data
        2. numpy ndarray containing depth measurments of real data
        3. float containing R² value
    """
    print("CALCULATING DDPLOT")
    df_X_cp = synthetic_data.copy(deep=True)
    df_Y_cp = real_data.copy(deep=True)
    print("encoding datasets...")
    for column in categorical_columns:
        df_X_cp[column] = __encode_categorical(df_X_cp, column)
        df_Y_cp[column] = __encode_categorical(df_Y_cp, column)
    df_Z = pd.concat([df_X_cp, df_Y_cp], axis=0, ignore_index=True)
    X_values = df_X_cp.values
    Y_values = df_Y_cp.values
    Z_values = df_Z.values
    Df_n, DG_m = __calculate_DD(X_values, Y_values, Z_values)
    # Calculating the R^2 value with respect to the reference line y=x
    x_data = DG_m
    y_data = Df_n
    y_pred = x_data  # Predicted values if y equals x
    r2 = r2_score(y_data, y_pred)
    __create_dd_plot(Df_n=Df_n, DG_m=DG_m, r2=r2).savefig(
        fname=f"{figures_path}/{g.ddplot_png_path}", dpi=300, format="png"
    )

    return Df_n, DG_m, r2


def __create_dd_plot(Df_n: np.ndarray, DG_m: np.ndarray, r2: float) -> plt:
    """
    Function to get matplotlib pyplot of Depth vs Depth plot of real and
        synthetic values.

        Args:
            Df_n: numpy ndarray containing depth measurments of synthetic data
            DG_m: numpy ndarray containing depth measurments of real data
            r2: float containing R² value

        Returns: matplotlib pyplot plot with Depth vs Depth Plot visualization
    """
    plt.figure()
    plt.scatter(DG_m, Df_n, color="#028692")
    plt.title("Depth vs Depth Plot")
    # Plotting the reference line y=x in the space where the data appears
    x_min = min(DG_m)
    x_max = max(DG_m)
    y_min = min(Df_n)
    y_max = max(Df_n)
    min_val = min(x_min, y_min)
    max_val = max(x_max, y_max)
    plt.plot([min_val, max_val], [min_val, max_val], color="#F05C80", linestyle="--")
    plt.text(
        min_val,
        max_val,
        f"$R^2 = {round(r2, 4)}$",
        verticalalignment="top",
        horizontalalignment="left",
    )
    plt.xlabel("Real Data")
    plt.ylabel("Synthetic Data")
    plt.tight_layout()
    return plt


def __prepare_data_for_tsn_transformation(
    real_data: pd.DataFrame, synthetic_data: pd.DataFrame
) -> (np.ndarray, np.ndarray):
    """
    Prepares data for tsne transformation
    Args:
        real_data: pandas Dataframe containing real sample set
        synthetic_data: pandas Dataframe containing synthetic sample set

    Returns: a transformed version of the input datasets adapted for TSNE transformation

    """
    # select numerical and categorical columns
    numerical_variables = real_data.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()
    categorical_variables = real_data.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    # preprocess numerical and categorical columns
    data_numerical_real = real_data[numerical_variables].values
    onehot_encoder = OneHotEncoder()
    data_categorical_real = onehot_encoder.fit_transform(
        real_data[categorical_variables]
    ).toarray()
    data_numerical_synthetic = synthetic_data[numerical_variables].values
    data_categorical_synthetic = onehot_encoder.transform(
        synthetic_data[categorical_variables]
    ).toarray()

    # return processed data
    real_data_prepared = np.column_stack((data_numerical_real, data_categorical_real))
    synthetic_data_prepared = np.column_stack(
        (data_numerical_synthetic, data_categorical_synthetic)
    )
    return real_data_prepared, synthetic_data_prepared


def tsne_transform(
    real_data: pd.DataFrame, synthetic_data: pd.DataFrame
) -> (pd.DataFrame, pd.DataFrame):
    """
    Get the T-SNE transformed datasets for real and synthetic.
    Non-linear statistical method for dimensionality reduction and visualizing
    high-dimensional data by giving each datapoint a location in a two or three-dimensional
    map.

    Note: Since sklearn T-SNE does not have a dedicated fit() method, only fit_transform,
    we used the openTSNE implementation that allows embedding new points into an
    existing embedding (https://opentsne.readthedocs.io/en/latest/index.html)

    Args:
        real_data: pandas DataFrame with real data
        synthetic_data: pandas DataFrame with synthetic

    Returns: a tuple with the real-transformed, synthetic-transformed datasets

    """

    prepared_data_real, prepared_data_synthetic = __prepare_data_for_tsn_transformation(
        real_data=real_data, synthetic_data=synthetic_data
    )

    # initialize and fit the tsne transformer
    tsne_transformer = TSNE(perplexity=30, verbose=True)
    embedding_real = tsne_transformer.fit(prepared_data_real)

    # transform real data
    tsne_real = pd.DataFrame(embedding_real, columns=["Component 1", "Component 2"])

    # transform synthetic data
    embedding_synthetic = embedding_real.transform(prepared_data_synthetic)
    tsne_synthetic = pd.DataFrame(
        embedding_synthetic, columns=["Component 1", "Component 2"]
    )

    # return transformed data
    return tsne_real, tsne_synthetic


def __tsn_visualization_data(
    real_data: pd.DataFrame,
    synthetic_data: pd.DataFrame,
    categorical_variables: List[str],
    binary_variables: List[str],
) -> (pd.DataFrame, pd.DataFrame):
    """
    Get tsn real and synthetic data for visualization
    Args:
        real_data: pandas Dataframe containing real sample set
        synthetic_data: pandas Dataframe containing synthetic sample set
        cathegorical_variables: list of the names of cathegorical variables
        binary-variables: list of the names of binary variables

    Returns: a tuple with the real-tsn, synthetic-tsn datasets
    """
    for col in categorical_variables:
        real_data[col] = real_data[col].astype("category")
        synthetic_data[col] = synthetic_data[col].astype("category")

    for col in binary_variables:
        real_data[col] = real_data[col].astype(bool)
        synthetic_data[col] = synthetic_data[col].astype(bool)

    tsne_real, tsne_synthetic = tsne_transform(
        real_data=real_data, synthetic_data=synthetic_data
    )
    tsne_real["label"] = "Real"
    tsne_synthetic["label"] = "Synthetic"

    return tsne_real, tsne_synthetic


def __isomap_visualization_data(
    prepared_data_real: pd.DataFrame, prepared_data_synthetic: pd.DataFrame
) -> (pd.DataFrame, pd.DataFrame):
    """
    Get isomap real and synthetic data for visualization
    Args:
        prepared_data_real: pandas Dataframe containing real tsn dataset
        prepared_data_synthetic: pandas Dataframe containing synthetic tsn dataset

    Returns: a tuple with the real-isomap, synthetic-isomap datasets
    """
    # initialize and fit the tsne transformer
    isomap_transformer = Isomap(n_components=2)

    # transform synthetic data
    isomap_values_real = isomap_transformer.fit_transform(prepared_data_real)
    isomap_real = pd.DataFrame(
        isomap_values_real, columns=["Component 1", "Component 2"]
    )
    isomap_real["label"] = "Real"

    # transform synthetic data
    isomap_values_synthetic = isomap_transformer.transform(prepared_data_synthetic)
    isomap_synthetic = pd.DataFrame(
        isomap_values_synthetic, columns=["Component 1", "Component 2"]
    )
    isomap_synthetic["label"] = "Synthetic"

    return isomap_real, isomap_synthetic


def __umap_visualization_data(
    prepared_data_real: pd.DataFrame, prepared_data_synthetic: pd.DataFrame
) -> (pd.DataFrame, pd.DataFrame):
    """
    Get umap real and synthetic data for visualization
    Args:
        prepared_data_real: pandas Dataframe containing real tsn dataset
        prepared_data_synthetic: pandas Dataframe containing synthetic tsn dataset

    Returns: a tuple with the real-umap, synthetic-umap datasets
    """

    # initialize and fit the tsne transformer
    umap_transformer = UMAP()

    # transform synthetic data
    umap_values_real = umap_transformer.fit_transform(prepared_data_real)
    umap_real = pd.DataFrame(umap_values_real, columns=["Component 1", "Component 2"])
    umap_real["label"] = "Real"

    # transform synthetic data
    umap_values_synthetic = umap_transformer.transform(prepared_data_synthetic)
    umap_synthetic = pd.DataFrame(
        umap_values_synthetic, columns=["Component 1", "Component 2"]
    )
    umap_synthetic["label"] = "Synthetic"

    return umap_real, umap_synthetic


def create_neighbour_graphs_figure(
    real_data: pd.DataFrame,
    synthetic_data: pd.DataFrame,
    categorical_variables: List[str],
    binary_variables: List[str],
    figures_path: str,
):
    tsne_real, tsne_synthetic = __tsn_visualization_data(
        real_data, synthetic_data, categorical_variables, binary_variables
    )
    prepared_real, prepared_synthetic = __prepare_data_for_tsn_transformation(
        real_data, synthetic_data
    )
    isomap_real, isomap_synthetic = __isomap_visualization_data(
        prepared_real, prepared_synthetic
    )
    umap_real, umap_synthetic = __umap_visualization_data(
        prepared_real, prepared_synthetic
    )

    graphs_data = {
        "tsne": [tsne_real, tsne_synthetic],
        "isomap": [isomap_real, isomap_synthetic],
        "umap": [umap_real, umap_synthetic],
    }

    tsne_isomap_umap_visualization_image(graphs_data).savefig(
        fname=f"{figures_path}/{g.vis_png_path}", dpi=300, format="png"
    )
