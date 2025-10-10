# -*- coding: utf-8 -*-
"""
    RAISE - RAI Synthetic Data Generator

    @author: Mikel Hernández Jiménez - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @author: Mikel Catalina Olazaguirre - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @version: 0.1
"""
# Stdlib imports

# Third-party app imports
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# Imports from your apps
import raise_synthetic_data_generator.sd_evaluation.evaluation_report.__global_variables__ as g
from raise_synthetic_data_generator.sd_evaluation.fidelity_metrics.visualizations import (
    plot_roc_curve,
)


def __prepare_data_for_classification(
    real_data: pd.DataFrame, synthetic_data: pd.DataFrame
) -> (np.ndarray, np.ndarray):
    """
    Combines both datasets into a single one where real data has label Real and synthetic has label Synthetic.
    Used to later on train a model to try to distinguish them

    Args:
        real_data: pandas Dataframe containing real sample set
        synthetic_data: pandas Dataframe containing synthetic sample set

    Returns: a tuple with both datasets appended and a label list containing whether each sample is Real/Synthetic

    """
    real_data["label"] = "Real"
    synthetic_data["label"] = "Synthetic"

    joined_data = pd.concat([real_data, synthetic_data]).sample(frac=1)

    labels = joined_data["label"].values
    input_data = joined_data.drop(columns=["label"], inplace=False)

    numerical_variables = input_data.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()
    data_numerical = StandardScaler().fit_transform(input_data[numerical_variables])

    categorical_variables = input_data.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()
    data_categorical = (
        OneHotEncoder().fit_transform(input_data[categorical_variables]).toarray()
    )

    input_data_processed = np.column_stack((data_numerical, data_categorical))

    real_data.drop(columns="label", inplace=True)
    synthetic_data.drop(columns="label", inplace=True)

    return input_data_processed, labels


def compute_distinguishability_metrics(
    real_data: pd.DataFrame,
    synthetic_data: pd.DataFrame,
    figures_path: str,
) -> (float, float):
    """
    This function trains a RandomForestClassifier to distinguish between real and synthetic samples.

    Args:
        real_data: pandas DataFrame containing real sample set.
        synthetic_data: pandas DataFrame containing synthetic sample set.

    Returns:
        auc_roc, propensity_score
    """
    # Combine and preprocess data
    input_data, labels = __prepare_data_for_classification(real_data, synthetic_data)

    # Convert labels to binary: 1 for real, 0 for synthetic
    binary_labels = np.where(labels == "Real", 1, 0)

    # Define the classification model
    model = RandomForestClassifier(
        n_estimators=1000,
        max_depth=3,
        random_state=64,
        oob_score=True,  # OOB score instead of roc_auc_score
        verbose=False,
    )

    # Train the classification model
    model.fit(input_data, binary_labels)

    # Get probability scores for ROC curve
    probability_scores = model.oob_decision_function_[:, 1]

    # Compute AUC-ROC
    auc_roc = model.oob_score_

    # Compute propensity score
    propensity_score = np.mean(probability_scores)

    # Generate ROC plot
    fig = plot_roc_curve(
        true_labels=binary_labels,
        probability_scores=probability_scores,
        auc_roc=auc_roc,
    )
    fig.savefig(fname=f"{figures_path}/{g.distinguish_png_path}", dpi=300, format="png")

    return auc_roc, propensity_score
