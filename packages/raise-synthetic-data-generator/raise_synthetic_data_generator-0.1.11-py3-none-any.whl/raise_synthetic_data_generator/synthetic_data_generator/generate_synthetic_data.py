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
import inspect
import traceback
from typing import Union
from pathlib import Path

# Third-party app imports
import pandas as pd
import optuna
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import LabelEncoder

# Imports from your apps
from raise_synthetic_data_generator.synthetic_data_generator.synthetic_data_generator import (
    SyntheticDataGenerator,
)
from raise_synthetic_data_generator.sd_evaluation.synthetic_data_evaluation import (
    SyntheticDataEvaluator,
)
from raise_synthetic_data_generator.custom_exceptions import SDGModelSelectionError
from raise_synthetic_data_generator import LogClass
from raise_synthetic_data_generator.utils.paths import prepare_output_folder


# ============================================
# GLOBAL CONSTANTS
# ============================================
AVAILABLE_MODELS = ["CTGAN", "TVAE", "Copulas", "auto-select"]
LOGGER = LogClass()

# ============================================
# CLASSES
# ============================================


# ============================================
# PUBLIC METHODS
# ============================================


def generate_synthetic_data(
    dataset: Union[str, pd.DataFrame],
    selected_model: str = "auto-select",
    n_samples: int = None,
    evaluation_report: bool = True,
    output_dir: Union[str, Path] = None,
    run_name: str = None,
):
    try:
        input_data = _load_dataset(dataset)
        LOGGER.log_info("Original data file read and validated!")

        LOGGER.log_info("Proceeding with output folder creation...")
        output_folder = _get_output_folder(output_dir, run_name)
        LOGGER.log_info("Output folder successfully created!")

        # Select synthetic data generation model
        LOGGER.log_info("Proceeding to model selection...")
        if selected_model == "auto-select":
            selected_model, parameters = _select_synthetic_data_generation_model(dataset=input_data)
        elif selected_model not in AVAILABLE_MODELS:
            raise SDGModelSelectionError(
                f"Selected model ({selected_model}) is not available"
            )
        LOGGER.log_info(f"{selected_model} model has been selected!")
        LOGGER.log_info("Proceeding with synthetic data generation...")

        # Generate and store synthetic data and model info
        if 'parameters' in locals():
            synthetic_data_generator = SyntheticDataGenerator(
                dataset=input_data, sdg_model=selected_model,parameters=parameters
            )
        else:
            synthetic_data_generator = SyntheticDataGenerator(
                dataset=input_data, sdg_model=selected_model
            )

        if n_samples is None:
            n_samples = len(input_data)
        synthetic_data = synthetic_data_generator.generate_synthetic_data(
            n_samples=n_samples
        )
        synthetic_data_path = output_folder / "synthetic_data.csv"
        if synthetic_data_path.exists():
            LOGGER.log_warning(f"File {synthetic_data_path.name} will be overwritten!")
        synthetic_data.to_csv(synthetic_data_path, index=False)
        # Store model info
        synthetic_data_generator.store_model_info(output_folder=output_folder)
        LOGGER.log_info(
            f"Synthetic data generated and saved successfully in: {output_folder}."
        )
        LOGGER.log_info("Proceeding with synthetic data evaluation...")

        # Evaluate synthetic data (optional)
        if evaluation_report:
            synthetic_data_evaluator = SyntheticDataEvaluator(
                original_dataset=input_data,
                synthetic_data=synthetic_data,
                output_folder=output_folder,
                information_text=synthetic_data_generator.get_model_info(),
            )
            synthetic_data_evaluator.evaluate_data()
        LOGGER.log_info(
            f"Synthetic data evaluation report generated and saved successfully in: {output_folder}."
        )

    except Exception as exception:
        # Log and raise the exception
        function_name = inspect.currentframe().f_code.co_name
        error_msg = (
            f"{function_name}() : An exception has occurred\n{traceback.format_exc()}"
        )
        LOGGER.log_error(error_msg)
        raise exception


# ============================================
# PRIVATE METHODS
# ============================================


def _select_synthetic_data_generation_model(dataset: pd.DataFrame):
    if dataset.shape[0] < 50: # Check if tehre is enough data at start, improves performance
            raise SDGModelSelectionError(message="there are not enough samples to train a model succesfully")

    def encode_strings(df):
        df = df.copy()
        for col in df.select_dtypes(include=['object', 'category']).columns:
            df[col] = LabelEncoder().fit_transform(df[col])
        return df
        
    def compute_score(real_data, synthetic_data):
        synthetic_data = synthetic_data.copy()
        real_data = real_data.copy()
        synthetic_data["label"] = 1
        real_data["label"] = 0

        all_data = pd.concat([synthetic_data, real_data], axis=0)
        all_data = encode_strings(all_data)
        train, test = train_test_split(all_data, test_size=0.2)

        classifier = RandomForestClassifier()
        classifier.fit(train.drop(["label"], axis=1), train["label"])
        pred_probs = classifier.predict_proba(test.drop(["label"], axis=1))[:, 1]

        return roc_auc_score(test["label"], pred_probs)
        
    def objective_function(trial):
        suggested_model = trial.suggest_categorical("SDG_model", ["CTGAN", "TVAE", "Copulas"])
        if suggested_model == "CTGAN":

            PAC = 10
            max_batch = min(512, dataset.shape[0] - dataset.shape[0] % PAC)
            suggested_parameters = {
                "epochs":trial.suggest_int("epochs",100,500),
                "batch_size": trial.suggest_int("batch_size", PAC, max_batch, step=PAC)
            }

            model = SyntheticDataGenerator(dataset=dataset,sdg_model=suggested_model,parameters=suggested_parameters)

        elif suggested_model == "TVAE":

            suggested_parameters = {
                "epochs": trial.suggest_int("epochs",100,500),
                "batch_size": trial.suggest_int("batch_size",1,dataset.shape[0])
            }

            model = SyntheticDataGenerator(dataset=dataset,sdg_model=suggested_model,parameters=suggested_parameters)

        elif suggested_model == "Copulas":

            suggested_parameters = {
                "enforce_rounding": trial.suggest_categorical("rounding",[True,False]),
                "enforce_min_max_values": trial.suggest_categorical("min_max",[True,False])
            }
                
            model = SyntheticDataGenerator(dataset=dataset,sdg_model=suggested_model,parameters=suggested_parameters)

        synthetic_samples = model.generate_synthetic_data(n_samples=dataset.shape[0])
        value = compute_score(real_data=dataset,synthetic_data=synthetic_samples)
            
        return abs(value - 0.5)
    study = optuna.create_study(direction='minimize')
    study.optimize(objective_function, n_trials=10)
    selected_model = study.best_params["SDG_model"]
    params = {k: v for k, v in study.best_params.items() if k != "SDG_model"}
    return selected_model, params


def _load_dataset(dataset: Union[str, pd.DataFrame]) -> pd.DataFrame:
    if isinstance(dataset, str):
        dataset_path = Path(dataset)
        if not dataset_path.exists():
            raise FileNotFoundError(f"Input file '{dataset}' does not exist.")
        if not dataset_path.is_file() or not dataset_path.stat().st_size:
            raise Exception(f"Input file '{dataset}' is not a valid, non-empty file.")
        try:
            input_data = pd.read_csv(dataset)
        except Exception as e:
            raise Exception(f"Failed to read input file '{dataset}': {e}")
    else:
        input_data = dataset.copy()
    return input_data


def _get_output_folder(output_dir, run_name):
    output_folder = prepare_output_folder(output_dir=output_dir, run_name=run_name)
    output_folder = Path(output_folder).resolve(strict=False)
    if not str(output_folder).startswith(str(Path.cwd().resolve())):
        raise ValueError("Invalid output_folder: directory traversal detected.")
    return output_folder


# ============================================
# MAIN BLOCK
# ============================================
