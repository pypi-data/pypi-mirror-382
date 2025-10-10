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
from sklearn.metrics import roc_curve

# Imports from your apps
import raise_synthetic_data_generator.sd_evaluation.evaluation_report.__global_variables__ as g


def tsne_isomap_umap_visualization_image(data_to_transform: dict) -> plt:
    """
    Function to get matplotlib pyplot of tsn, umap and isomap visualization images of real and
    synthetic values.

    Args:
        real_data: pandas Dataframe containing real sample set
        synthetic_data: pandas Dataframe containing synthetic sample set
        cathegorical_variables: list of the names of cathegorical variables
        binary-variables: list of the names of binary variables

    Returns: matplotlib pyplot plot with three visualizations
    """
    tsne_real, tsne_synthetic = data_to_transform["tsne"]
    isomap_real, isomap_synthetic = data_to_transform["isomap"]
    umap_real, umap_synthetic = data_to_transform["umap"]

    plt.figure(figsize=(12, 4))
    # using subplot function and creating plot one
    # TSNE
    plt.subplot(1, 3, 1)  # row 1, column 3, count 1
    plt.scatter(
        tsne_real["Component 1"], tsne_real["Component 2"], c="#028692", alpha=0.5
    )
    plt.scatter(
        tsne_synthetic["Component 1"],
        tsne_synthetic["Component 2"],
        c=["#F05C80"],
        alpha=0.5,
    )
    plt.title("t-SNE (openTSNE)")
    plt.xticks([])
    plt.yticks([])
    plt.grid(True, linestyle="--", color="gray", alpha=0.2, zorder=0)

    # using subplot function and creating plot two
    # ISOMAP
    plt.subplot(1, 3, 2)
    plt.scatter(
        isomap_real["Component 1"],
        isomap_real["Component 2"],
        label="Real data",
        c="#028692",
        alpha=0.5,
    )
    plt.scatter(
        isomap_synthetic["Component 1"],
        isomap_synthetic["Component 2"],
        label="Synthetic data",
        c=["#F05C80"],
        alpha=0.5,
    )
    plt.title("Isomap")
    plt.legend(loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.4))
    plt.xticks([])
    plt.yticks([])
    plt.grid(True, linestyle="--", color="gray", alpha=0.2, zorder=0)

    # UMAP
    plt.subplot(1, 3, 3)
    plt.scatter(
        umap_real["Component 1"], umap_real["Component 2"], c="#028692", alpha=0.5
    )
    plt.scatter(
        umap_synthetic["Component 1"],
        umap_synthetic["Component 2"],
        c=["#F05C80"],
        alpha=0.5,
    )
    plt.title("UMAP")
    plt.xticks([])
    plt.yticks([])
    plt.grid(True, linestyle="--", color="gray", alpha=0.2, zorder=0)

    # space between the plots
    plt.tight_layout()

    # show plot
    return plt


def plot_roc_curve(true_labels: list, probability_scores: list, auc_roc: float):
    figure = plt.figure(figsize=(10, 5))

    fpr, tpr, _ = roc_curve(true_labels, probability_scores, pos_label=1)
    plt.plot(fpr, tpr, color="#028692", label=f"AUC-ROC = {auc_roc}")
    plt.fill_between(fpr, tpr, color="#028692", alpha=0.4)

    plt.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        color="#F05C80",
        label="Ideal result (random classification)",
    )
    plt.xlim([-0.01, 1.01])
    plt.ylim([-0.01, 1.01])

    plt.ylabel("True Positive Rate")
    plt.xlabel("False Positive Rate")
    plt.title("ROC Curve")

    plt.legend()

    figure.tight_layout()
    return figure


def hellinger_distance_per_variable(hellinger_distances: dict, mean_hellinger: float):
    """
    Function to get matplotlib pyplot of Hellinger Distance per Variable visualization
    image of real and synthetic values.

    Args:
        hellinger_distances: dictionary containing Hellinger Distance between
        synthetic and real data per variable
        mean_hellinger: float value containing mean Hellinger Distance of the datasets

    Returns: matplotlib pyplot plot with Hellinger Distance per Variable visualization
    """
    figure, ax = plt.subplots()

    ax.set_title("Hellinger Distance per variable")
    ax.bar(
        list(hellinger_distances.keys()),
        list(hellinger_distances.values()),
        color="#028692",
    )

    # Ajustar los límites del eje y
    ax.set_ylim(0, 1)
    ax.set_xticklabels(hellinger_distances.keys(), rotation=90)
    ax.hlines(
        mean_hellinger,
        0,
        len(hellinger_distances) - 1,
        colors="#F05C80",
        linestyles="--",
        label="Mean Hellinger Distance",
    )
    ax.legend()
    ax.grid(True, axis="y", linestyle="--", linewidth=0.5)
    figure.tight_layout()
    return figure


# def privacy_attacks_visualization(four_attacks_values, inf_eval_values, path1, path2):
#     """
#     Function to save matplotlib pyplot of privacy attacks visualizations images
#     of real and synthetic values.


#     Args:
#         four_attacks_values: pandas dataframe containing every attack risk and interval of confidence
#         inf eval_values: pandas dataframe containing inference attack risk per variable
#         path1: string containing the path (including name) to save the first visualization
#         path2: string containing the path (including name) to save the second visualization

#     """

#     four_attacks_values.rename(columns={"value": "Risk"}, inplace=True)

#     # all atacks figure
#     values = four_attacks_values["Risk"]
#     index = four_attacks_values.index
#     error = [[], []]
#     for elem in four_attacks_values["ci"]:
#         error[0].append(elem[0])
#         error[1].append(elem[1])

#     # plt.figure()
#     # fig, ax = plt.subplots()
#     # ax.errorbar(index,
#     #             values,
#     #             yerr=error,
#     #             fmt='o', ecolor='red', capsize=5, capthick=2, marker='.', markersize=7)

#     # Customize plot
#     plt.figure()
#     fig, ax = plt.subplots()
#     # fig.set_size_inches(10, 6)
#     sns.scatterplot(x=index, y="Risk", data=four_attacks_values, color="black", ax=ax)
#     plt.xticks(rotation=45)
#     plt.xlabel(None)

#     plt.title("Attacks risk with Confidence Intervals")
#     plt.errorbar(
#         index,
#         values,
#         yerr=(values - error[0], error[1] - values),
#         fmt="o",
#         color="black",
#     )
#     # Show plot
#     plt.tight_layout()
#     plt.savefig(path1, dpi=300)

#     # inference attack results
#     plt.figure()
#     plt.title("Inference Evaluator attack risk per variable")
#     plt.bar(inf_eval_values["Secret"], inf_eval_values["Risk"])

#     # Ajustar los límites del eje y
#     plt.ylim(0, 1)
#     plt.xticks(rotation=90)
#     plt.tight_layout()
#     plt.savefig(path2, dpi=300)


def DD_plot(Df_n: np.ndarray, DG_m: np.ndarray, r2: float) -> plt:
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


def trtr_tstr_visualizations(results_trtr, results_tstr, result_diff, classification):
    if classification:
        eval = "accuracy"
    else:
        eval = "RMSE"

    # Crear una figura con dos subplots (una fila, dos columnas)
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))

    # Configurar el ancho de las barras
    bar_width = 0.35

    # Configurar la posición de las barras en el eje X
    r1 = range(len(results_trtr))
    r2 = [x_val + bar_width for x_val in r1]

    # Primer gráfico de barras
    ax[0].bar(r1, results_trtr[eval], width=bar_width, edgecolor="white", label="TRTR")
    ax[0].bar(r2, results_tstr[eval], width=bar_width, edgecolor="white", label="TSTR")

    # Añadir etiquetas, título y leyenda al primer gráfico
    ax[0].set_xlabel("Model")
    ax[0].set_ylabel(eval)
    ax[0].set_xticks([r_val + bar_width / 2 for r_val in range(len(results_trtr))])
    ax[0].set_xticklabels(results_trtr["model"])
    ax[0].set_title("Comparison of Model {} between TRTR and TSTR".format(eval))
    ax[0].legend()
    ax[0].grid(True, axis="y", linestyle="--", linewidth=0.5)
    ylim = ax[0].get_ylim()

    # Segundo gráfico de dispersión
    ax[1].scatter(result_diff["model"], result_diff[eval + "_diff"], label="Difference")
    ax[1].plot(
        result_diff["model"], result_diff[eval + "_diff"], linestyle="-", marker="o"
    )

    # Añadir etiquetas, título y leyenda al segundo gráfico
    ax[1].set_xlabel("Model")
    ax[1].set_ylabel(eval + " difference")
    ax[1].set_xticks(range(len(result_diff)))
    ax[1].set_xticklabels(result_diff["model"])
    ax[1].set_title("Difference of Model {} between TRTR and TSTR".format(eval))
    ax[1].set_ylim(ylim)
    ax[1].legend()

    # Añadir líneas de cuadrícula al segundo gráfico
    ax[1].grid(True, axis="y", linestyle="--", linewidth=0.5)

    # Ajustar el diseño para evitar la superposición de etiquetas
    fig.tight_layout()

    # Guardar la figura combinada
    fig.savefig(
        g.trtr_tstr_results_png_path, dpi=300, bbox_inches="tight", format="png"
    )
