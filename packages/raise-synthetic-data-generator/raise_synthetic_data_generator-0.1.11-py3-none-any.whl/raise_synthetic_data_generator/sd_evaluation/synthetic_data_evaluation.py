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
from importlib import resources as ir

# Third-party app imports
import pandas as pd
from visions import typesets
from visions.functional import infer_type

# Imports from your apps
from raise_synthetic_data_generator import LogClass
from raise_synthetic_data_generator.sd_evaluation.fidelity_metrics.correlations import (
    pairwise_correlation_difference,
)
from raise_synthetic_data_generator.sd_evaluation.fidelity_metrics.distributions import (
    hellinger_distances,
)
from raise_synthetic_data_generator.sd_evaluation.fidelity_metrics.ml_metrics import (
    compute_distinguishability_metrics,
)
from raise_synthetic_data_generator.sd_evaluation.fidelity_metrics.statistical_tests import (
    chi_square,
    mann_whitney,
)
from raise_synthetic_data_generator.sd_evaluation.fidelity_metrics.dimensionality_reduction import (
    ddplot,
    create_neighbour_graphs_figure,
)
from raise_synthetic_data_generator.sd_evaluation.evaluation_report.report import (
    generate_pdf_report,
)


# ============================================
# GLOBAL CONSTANTS
# ============================================

# ============================================
# CLASSES
# ============================================


class SyntheticDataEvaluator(LogClass):
    def __init__(
        self,
        original_dataset: pd.DataFrame,
        synthetic_data: pd.DataFrame,
        output_folder: str,
        information_text: str,
    ):
        super().__init__()
        self.original_dataset = original_dataset
        self.synthetic_dataset = synthetic_data
        self.evaluation_report_path = str(output_folder / "evaluation_report.pdf")

        figures_path = output_folder / "evaluation_figures"
        figures_path.mkdir(parents=True, exist_ok=True)

        self.figures_path = str(figures_path)
        self.information_text = information_text

        self.log_info("Infering variable types from dataset")
        self.__infer_variable_types_from_dataset()
        self.log_info("Variables types inferred from dataset!")
        self.__basic_data_transformation()

    def __infer_variable_types_from_dataset(self):
        self.numerical_variables = []
        self.categorical_variables = []
        self.binary_variables = []

        typeset = typesets.StandardSet()

        # Infer column types of dataset
        for column in self.original_dataset.columns.tolist():
            if str(infer_type(self.original_dataset[column], typeset)) == "Float":
                self.numerical_variables.append(column)
            elif str(infer_type(self.original_dataset[column], typeset)) == "Integer":
                if len(self.original_dataset[column].value_counts().values) == 2:
                    self.binary_variables.append(column)
                elif len(self.original_dataset[column].value_counts().values) <= 10:
                    self.categorical_variables.append(column)
                else:
                    self.numerical_variables.append(column)
            elif str(infer_type(self.original_dataset[column], typeset)) == "String":
                self.categorical_variables.append(column)
            elif str(infer_type(self.original_dataset[column], typeset)) == "Boolean":
                self.binary_variables.append(column)

    def __basic_data_transformation(self):
        all_variables = (
            self.numerical_variables
            + self.categorical_variables
            + self.binary_variables
        )

        for column in self.original_dataset.columns.tolist():
            if column in all_variables:
                if (
                    column in self.categorical_variables
                    or column in self.binary_variables
                ):
                    self.original_dataset[column] = self.original_dataset[
                        column
                    ].astype("category")
                    self.synthetic_dataset[column] = self.synthetic_dataset[
                        column
                    ].astype("category")
            else:
                self.original_dataset.drop(columns=[column], inplace=True)
                self.synthetic_dataset.drop(columns=[column], inplace=True)

    def __evaluate_data_fidelity(self):
        # fidelity_evaluation_table_path = Path(
        #     Path(__file__).parent, "fidelity_evaluation_table.csv"
        # )
        pkg_data = "raise_synthetic_data_generator.sd_evaluation"
        csv_name = "fidelity_evaluation_table.csv"

        with ir.open_text(
            pkg_data, csv_name, encoding="utf-8"
        ) as fidelity_evaluation_table_path:
            fidelity_evaluation_table = pd.read_csv(fidelity_evaluation_table_path)

        # compute hellinger distances
        hellinger_dist_per_col, hellinger_dist_mean = hellinger_distances(
            real_data=self.original_dataset,
            synthetic_data=self.synthetic_dataset,
            figures_path=self.figures_path,
        )

        # perform mann whitney tests for numerical variables
        m_w_per_col, mann_whitney_th_rate = mann_whitney(
            real_data=self.original_dataset[self.numerical_variables],
            synthetic_data=self.synthetic_dataset[self.numerical_variables],
            significance_level=0.1,
        )

        # perform chi square for binary and categorical variables
        binary_and_categorical_variables = (
            self.binary_variables + self.categorical_variables
        )
        chi_sq_p_values, chi_sq_variables_proportion = chi_square(
            real_data=self.original_dataset[binary_and_categorical_variables],
            synthetic_data=self.synthetic_dataset[binary_and_categorical_variables],
            significance_level=0.1,
        )

        # compute pairwise correlation difference
        correlation_difference, correlation_figure = pairwise_correlation_difference(
            real_data=self.original_dataset,
            synthetic_data=self.synthetic_dataset,
            figures_path=self.figures_path,
        )

        # compute dd-plot and neighbour graphs
        Df_n, DG_m, r2 = ddplot(
            synthetic_data=self.synthetic_dataset,
            real_data=self.original_dataset,
            categorical_columns=binary_and_categorical_variables,
            figures_path=self.figures_path,
        )
        create_neighbour_graphs_figure(
            real_data=self.original_dataset,
            synthetic_data=self.synthetic_dataset,
            categorical_variables=self.categorical_variables,
            binary_variables=self.binary_variables,
            figures_path=self.figures_path,
        )

        # Compute ml metrics
        ml_au_roc, ml_propensity_score = compute_distinguishability_metrics(
            real_data=self.original_dataset,
            synthetic_data=self.synthetic_dataset,
            figures_path=self.figures_path,
        )

        # Gather results
        metrics_results = {
            "Hellinger Distance": hellinger_dist_mean,
            "Mann_whittney": mann_whitney_th_rate,
            "Chi-squared": chi_sq_variables_proportion,
            "Correlations (PCD)": correlation_difference,
            "DD-Plot": r2,
            "AUC-ROC": ml_au_roc,
            "Propensity score": ml_propensity_score,
        }
        fidelity_evaluation_table["Value"] = metrics_results.values()

        self.fidelity_results = {
            "evaluation-table": fidelity_evaluation_table,
            "hellinger-table": hellinger_dist_per_col,
            "m-w-table": m_w_per_col,
            "chi-square-table": chi_sq_p_values,
            "cors-comparison": correlation_figure,
        }

    def evaluate_data(self):
        self.__evaluate_data_fidelity()
        # self.__evaluate_data_privacy()
        generate_pdf_report(
            fidelity_metrics=self.fidelity_results,
            filename=self.evaluation_report_path,
            information_text=self.information_text,
            figures_path=self.figures_path,
        )


# ============================================
# PUBLIC METHODS
# ============================================


# ============================================
# PRIVATE METHODS
# ============================================


# ============================================
# MAIN BLOCK
# ============================================
