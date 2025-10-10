# -*- coding: utf-8 -*-
"""
    RAISE - RAI Synthetic Data Generator

    @author: Mikel Hernández Jiménez - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @author: Mikel Catalina Olazaguirre - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @version: 0.1
"""
# Stdlib imports
from importlib.resources import files, as_file

# Third-party app imports
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    PageBreak,
    NextPageTemplate,
    Image,
    Spacer,
    Paragraph,
    PageTemplate,
    Frame,
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.tables import Table
from typing import Optional

# Imports from your apps
from raise_synthetic_data_generator.sd_evaluation.evaluation_report.ReportTemplate import (
    ReportTemplate,
)
from raise_synthetic_data_generator.sd_evaluation.evaluation_report.pdf_styles.paragraph_styles import (
    get_paragraph_styles,
)
from raise_synthetic_data_generator.sd_evaluation.evaluation_report.pdf_styles.table_styles import (
    get_table_styles,
)
import raise_synthetic_data_generator.sd_evaluation.evaluation_report.__global_variables__ as g


# def __get_logo_path():
#     res = ir.files("raise_synthetic_data_generator.sd_evaluation.evaluation_report.images").joinpath("EOSC-RAISE.png")
#     with as_file(res) as p:
#         return str(p)


def __get_logo_image():
    pkg = "raise_synthetic_data_generator.sd_evaluation.evaluation_report.images"
    res = files(pkg).joinpath("EOSC-RAISE.png")
    # as_file materializa el recurso aunque esté en un wheel/zip
    with as_file(res) as img_path:
        return str(img_path)


def __page(canvas: Canvas, doc):
    """
    Create header and footer of a page with raise logo and number of page
    """
    canvas.saveState()
    canvas.drawImage(
        image=__get_logo_image(),
        x=inch * 0.8,
        y=A4[1] - 1.5 * inch,
        width=inch * 1.2,
        preserveAspectRatio=True,
    )
    canvas.setFont("Helvetica", 9)
    canvas.drawString(A4[0] - inch, 0.75 * inch, "%d" % doc.page)
    canvas.restoreState()


def __cover(canvas: Canvas, doc):
    """
    Create header and footer of a page with raise logo and number of page
    """
    blueRGB = (15 / 300, 23 / 300, 42 / 300)
    xtext = A4[0] / 2.9
    ytext = 8 * inch
    linewidth = 5 * inch

    canvas.saveState()

    # Draw blue rectangle
    canvas.setStrokeColorRGB(blueRGB[0], blueRGB[1], blueRGB[2])
    canvas.setLineWidth(linewidth)
    canvas.line(0, 0, 0, A4[1])

    # Write blue title
    canvas.setFont("Helvetica-Bold", 45)
    canvas.setFillColorRGB(blueRGB[0], blueRGB[1], blueRGB[2])
    canvas.drawString(xtext, ytext, "Synthetic data")
    ytext -= 42
    canvas.drawString(xtext, ytext, "Evaluation")
    ytext -= 42
    canvas.drawString(xtext, ytext, "Report")
    ytext -= 42 * 5

    # Add image below the text
    # image_path = "/src/raise_synthetic_data_generator/sd_evaluation/evaluation_report/images/EOSC-RAISE.png"
    # pkg = "raise_synthetic_data_generator.sd_evaluation.evaluation_report.images"
    # img_name = "EOSC-RAISE.png"
    image_width = 350  #
    image_height = 130  #
    x_image = xtext  #
    y_image = ytext + 35

    # raise_logo = __get_logo_image()
    raise_logo = __get_logo_image()
    canvas.drawImage(
        raise_logo,
        x_image,
        y_image,
        width=image_width,
        height=image_height,
        mask="auto",
    )

    # Write date and other specifications
    canvas.setFont("Helvetica-Bold", 10)
    canvas.setFillColorRGB(0, 0, 0)
    canvas.drawString(xtext, ytext, "Date:")
    now_formatted = datetime.now().strftime("%Y/%m/%d")
    canvas.setFont("Helvetica", 10)
    canvas.drawString(
        xtext + stringWidth("Date: ", "Helvetica-Bold", 10), ytext, now_formatted
    )
    ytext -= 12

    canvas.restoreState()


def __all_metrics_list(dict_list, metrics_list, real_data):
    """
    Returns a list of lists with all the metrics and their results of each cathegorical variable.
    If a metric does not have a result for a cathegorical variable the result will be N/A

    Args:
        - dict_list: list of dicts. Every dict will be related to one metric and will contain
                     the results of some or every cathegorical variables
        - metrics_list: list of the names of the metrics used
        - real_data: pandas dataFrame containing real sample set

    Returns: a list of lists with all the metrics (including their names) and their results
             on each cathegorical variable
    """
    metrics = dict()

    for column in real_data.columns.tolist():
        metrics[column] = []

    for dl in dict_list:
        for key in metrics.keys():
            if dl.get(key) is None:
                metrics[key].append("N/A")
            else:
                metrics[key].append(round(dl[key], 4))

    # insert names of cathegorical variables to values list
    [metrics[key].insert(0, key) for key in metrics.keys()]
    metric_result = list(metrics.values())

    # instert names of the metrics
    metrics_list.insert(0, "Variables")
    metric_result.insert(0, metrics_list)

    return metric_result


def __get_image(path: str, height, halign="CENTER"):
    """
    Get the Image of the specified path with the specified height and
    preserved aspect ratio (hAlign can be specified as well)

    Args:
        path: path of the image (str)
        height: height of the Image object (float)
        halign: alignment of the image (CENTER, LEFT or RIGHT)

    Returns: the Image object of the specified image with preserved aspect ratio
    """
    img = ImageReader(path)
    iw, ih = img.getSize()
    aspect = iw / float(ih)
    return Image(path, width=(height * aspect), height=height, hAlign=halign)


def add_text(elements: list, text: str, num: int, par_styles: dict):
    aux = num
    for elem in text:
        if elem[0]:
            if "{}" in elem[1]:
                elements.append(
                    Paragraph(elem[1].format(aux), style=par_styles["bullet"])
                )
                aux += 1
            else:
                elements.append(Paragraph(elem[1], style=par_styles["bullet"]))
        else:
            if "{}" in elem[1]:
                elements.append(
                    Paragraph(elem[1].format(aux), style=par_styles["normal"])
                )
                aux += 1
            else:
                elements.append(Paragraph(elem[1], style=par_styles["normal"]))


def __get_report_table_list(
    report_table: pd.DataFrame, par_style: ParagraphStyle, extra: Optional[str] = None
) -> list:
    """
    Get report_table values in a list.
    Changes the text to type Paragraph with the specified style

    Args:
        - report_table: data to be changed to Paragraph style, pd.DataFrame
        - par_style: ParagraphStyle for the Paragraph types
        - eval: integer to define evaluation (fidelity = 1, utility = 2, privacy = 3)
        - extra: string to differentiate regression from classification in Utility evaluation

    Returns: report_table values in a list and with Paragraph types for the text
    """
    # get report_table values and column names
    table_columnames = report_table.columns.values.tolist()
    table_values = report_table.values.tolist()

    # change report table types to Paragraph except for the float types
    def_list = []
    errors = False
    for elem in table_values:
        aux2 = []
        for element_number in range(len(elem)):
            if extra is not None and element_number == 5:
                text = elem[element_number].format(extra)
                text = text[0].upper() + text[1:]
                aux2.append(Paragraph(text, style=par_style))
            elif element_number != 5:
                aux2.append(Paragraph(elem[element_number], style=par_style))
            else:
                if elem[element_number] is None:
                    aux2.append("N/A*")
                    errors = True
                else:
                    aux2.append(round(elem[element_number], 4))
        def_list.append(aux2)

    if def_list == []:
        return None, None

    def_list.insert(0, table_columnames)  # insert column names
    return def_list, errors


def __add_distribution_text(elements, mann_whitney, chi, table_num, par_styles):
    if mann_whitney and chi:
        elements.append(
            Paragraph(g.distribution_introduction_text_both, style=par_styles["normal"])
        )
        add_text(elements, g.distribution_text_mann, table_num, par_styles)
        elements.append(Paragraph("<br/><br/>", par_styles["normal"]))
        add_text(elements, g.distribution_text_chi, table_num, par_styles)
        elements.append(
            Paragraph(
                g.distribution_text_conclusion.format(
                    "Both of the statistical tests have", table_num, "these tests"
                ),
                style=par_styles["normal"],
            )
        )
    elif mann_whitney:
        elements.append(
            Paragraph(
                g.distribution_introduction_text_one.format(g.mann_metric),
                style=par_styles["normal"],
            )
        )
        add_text(elements, g.distribution_text_mann, table_num, par_styles)
        elements.append(
            Paragraph(
                g.distribution_text_conclusion.format(
                    "The statictical test has", table_num, "this test"
                ),
                style=par_styles["normal"],
            )
        )
    else:
        elements.append(
            Paragraph(
                g.distribution_introduction_text_one.format(g.chi_metric),
                style=par_styles["normal"],
            )
        )
        add_text(elements, g.distribution_text_chi, table_num, par_styles)
        elements.append(
            Paragraph(
                g.distribution_text_conclusion.format(
                    "The statictical test has", table_num, "this test"
                ),
                style=par_styles["normal"],
            )
        )
    table_num += 1


def build_pdf(doc: ReportTemplate, elements: list):
    doc.multiBuild(elements)


def generate_pdf_report(
    fidelity_metrics: dict, filename: str, information_text: str, figures_path: str
):
    """
    Generates and saves pdf report
    """
    figure_num = 1
    table_num = 1

    results_f, results_u, results_p = None, None, None

    indented_1 = ParagraphStyle("indented_1", leftIndent=20)

    indented_2 = ParagraphStyle("indented_2", leftIndent=40)

    # create the document
    doc = ReportTemplate(
        filename=filename,
        rightMargin=0,
        leftMargin=0,
        topMargin=0,
        bottomMargin=0,
        title=g.documentTitle,
        author=g.author,
    )

    fidelity_metrics["evaluation-table"] = fidelity_metrics["evaluation-table"].drop(
        columns=["Category"]
    )

    # create frame and pageTemplate
    frameN = Frame(inch, inch, 451, 697, id="normal")
    frameTable = Frame(0, inch, A4[0], 697, id="table", leftPadding=0)
    templatecover = PageTemplate(id="cover", frames=frameN, onPage=__cover)
    template = PageTemplate(id="standard", frames=frameN, onPage=__page)
    tableTemplate = PageTemplate(id="table", frames=[frameN, frameTable], onPage=__page)
    doc.addPageTemplates([templatecover, template, tableTemplate])

    # get defined styles
    par_styles = get_paragraph_styles()

    standard_table_style = get_table_styles("standard")
    # left_table_style = get_table_styles("left")
    span_table_sytle = get_table_styles("span")
    top_table_style = get_table_styles("top")

    # FLOWABLE
    elements = []  # all the elements of the pdf will be added to this list

    # set standart page template to the pages
    elements.append(NextPageTemplate("cover"))
    elements.append(NextPageTemplate("standard"))

    elements.append(PageBreak())

    # TABLE OF CONTENTS
    elements.append(Paragraph("Table of contents", style=par_styles["title"]))
    toc = TableOfContents(dotsMinLevel=0)
    toc.levelStyles = par_styles["toc"]
    elements.append(toc)
    # elements.append(NextPageTemplate('table'))

    elements.append(PageBreak())
    elements.append(Paragraph("Notes", style=par_styles["title"]))
    elements[-1].keepWithNext = False
    lines = information_text.split("\n")
    in_training_params = False

    for line in lines:
        stripped = line.strip()

        # Línea vacía
        if not stripped:
            elements.append(Spacer(1, 12))
            continue

        # 👉 LINKS (poner esto antes de los guiones y training_params)
        if "http" in stripped and stripped.startswith("-"):
            url = stripped[2:].strip()
            link_html = f'<a href="{url}" color="blue">{url}</a>'
            elements.append(Paragraph(link_html, style=indented_1))
            continue

        if stripped.startswith("http"):
            link_html = f'<a href="{stripped}" color="blue">{stripped}</a>'
            elements.append(Paragraph(link_html, style=par_styles["normal"]))
            continue

        # Línea que inicia el bloque de parámetros
        if "Training parameters" in stripped:
            in_training_params = True
            elements.append(Paragraph(stripped, style=indented_1))
            continue

        # Dentro del bloque de training params con doble indentación
        if in_training_params and stripped.startswith("-"):
            elements.append(Paragraph(stripped, style=indented_2))
            continue

        # Cualquier otro caso indentado
        if stripped.startswith("-") or in_training_params:
            elements.append(Paragraph(stripped, style=indented_1))
            continue

        # Reinicio al llegar a References
        if stripped.startswith("References"):
            in_training_params = False
            elements.append(Spacer(1, 12))
            elements.append(Paragraph(stripped, style=par_styles["normal"]))
            continue

        # Normal o título
        elements.append(Paragraph(stripped, style=par_styles["normal"]))
    elements.append(PageBreak())

    # FIDELITY
    # if any(value for value in fidelity_metrics.values()):
    report_table_fidelity = fidelity_metrics["evaluation-table"]
    mann_whitney_p_values = fidelity_metrics["m-w-table"]
    chi_squared_p_values = fidelity_metrics["chi-square-table"]

    fidelity_title = Paragraph(g.fidelity, style=par_styles["h1"])
    elements.append(fidelity_title)
    elements[-1].keepWithNext = True

    #   FIDELITY METRICS SUMMARY
    report_list, errors = __get_report_table_list(
        report_table=report_table_fidelity, par_style=par_styles["left_small"]
    )
    if report_list is not None:
        elements.append(Paragraph(g.fidelity_summary, style=par_styles["h2"]))
        elements[-1].keepWithNext = True
        t1 = Table(
            report_list,
            style=standard_table_style,
            colWidths=[
                # inch * 0.95,
                inch * 0.85,
                2 * inch,
                0.75 * inch,
                0.74 * inch,
                1.7 * inch,
                0.50 * inch,
            ],
        )
        elements.append(t1)
        if errors:
            elements[-1].keepWithNext = True
            elements.append(
                Paragraph(
                    "*An error occurred while evaluating dataset with this metric",
                    style=par_styles["normal"],
                )
            )

    #   VISUALIZATIONS SECTION
    # elements.append(FrameBreak())
    elements.append(Paragraph(g.visualizations_section, style=par_styles["h2"]))
    elements[-1].keepWithNext = True

    #       DISTRIBUTIONS
    elements.append(Paragraph(g.distribution, style=par_styles["h3"]))
    elements[-1].keepWithNext = True

    # HELLINGER DISTANCE
    elements.append(Paragraph(g.hellinger_distances, style=par_styles["h4"]))
    elements[-1].keepWithNext = True
    add_text(elements, g.hellinger_text, figure_num, par_styles)

    elements.append(__get_image(f"{figures_path}/{g.hellinger_png_path}", 7 * cm))
    elements.append(
        Paragraph(
            f"Figure {figure_num}: Hellinger distances per variable",
            style=par_styles["center_small"],
        )
    )
    figure_num += 1
    elements.append(Spacer(1, 20))

    # STATISTICAL TESTS
    elements.append(Paragraph(g.statistical_tests, style=par_styles["h4"]))
    elements[-1].keepWithNext = True
    add_text(elements, g.distribution_text, table_num, par_styles)

    elements.append(
        Table(
            __chi_mann_whitney_tables(
                mann_whitney_p_values,
                chi_squared_p_values,
                span_table_sytle,
                num=table_num,
                par_styles=par_styles,
            ),
            style=top_table_style,
        )
    )
    elements.append(Spacer(0, 20))

    #   VISUALIZATIONS SECTION
    # if any(selected and elem != g.auc_metric and elem != g.propensity_metric
    #     for elem, selected in fidelity_metrics.items()):
    #         elements.append(Paragraph(g.visualizations_section, style = par_styles['h2']))
    #         elements[-1].keepWithNext = True

    #       CORRELATION COMPARISON
    # if fidelity_metrics["cors-comparison"]:
    elements.append(Paragraph(g.cors_comparison, style=par_styles["h3"]))
    elements[-1].keepWithNext = True
    add_text(elements, g.correlation_text, figure_num, par_styles)
    elements.append(__get_image(f"{figures_path}/{g.cors_png_path}", 7 * cm))
    elements.append(
        Paragraph(
            f"Figure {figure_num}: Correlation comparison",
            style=par_styles["center_small"],
        )
    )
    figure_num += 1
    elements.append(Spacer(1, 20))
    # AUC-ROC #
    elements.append(Paragraph("Distinguishability", style=par_styles["h4"]))
    elements[-1].keepWithNext = True
    add_text(elements, g.distinguishability_text, figure_num, par_styles)
    elements.append(__get_image(f"{figures_path}/{g.distinguish_png_path}", 7 * cm))
    elements.append(
        Paragraph(
            f"Figure {figure_num}:AUC-ROC",
            style=par_styles["center_small"],
        )
    )
    figure_num += 1
    # #       DIMENSIONALITY REDUCTION
    # if fidelity_metrics[g.ddplot_metric] or fidelity_metrics[g.tsne_metric]:
    elements.append(Paragraph(g.dimensionality, style=par_styles["h3"]))
    elements[-1].keepWithNext = True

    #     if fidelity_metrics[g.ddplot_metric]:
    #         #           DDPlot
    #         if fidelity_errors.get(g.ddplot_metric) is False:
    elements.append(Paragraph(g.dd_plot, style=par_styles["h4"]))
    elements[-1].keepWithNext = True
    elements.append(
        Paragraph(g.dd_plot_text.format(figure_num), style=par_styles["normal"])
    )
    elements[-1].keepWithNext = True
    elements.append(__get_image(f"{figures_path}/{g.ddplot_png_path}", 7 * cm))
    elements.append(
        Paragraph(
            f"Figure {figure_num}: Depth vs Depth plot",
            style=par_styles["center_small"],
        )
    )
    figure_num += 1

    #     #           T-SNE,ISOMAP,UMAP
    #     if fidelity_metrics[g.tsne_metric]:
    #         if fidelity_errors.get(g.tsne_metric) is False:
    elements.append(Paragraph(g.neighbour, style=par_styles["h4"]))
    elements[-1].keepWithNext = True
    add_text(elements, g.tsne_text, figure_num, par_styles)
    elements.append(__get_image(f"{figures_path}/{g.vis_png_path}", 6 * cm))
    elements.append(
        Paragraph(
            f"Figure {figure_num}: t-SNE, ISOMAP, UMAP visualizations",
            style=par_styles["center_small"],
        )
    )
    figure_num += 1

    elements.append(PageBreak())

    doc.multiBuild(elements)
    return results_f, results_u, results_p


def __chi_mann_whitney_tables(mann_d, chi_d, table_style, num, par_styles, alpha=0.2):
    """
    Returns a list of lists with all the metrics and their results of each categorical variable.
    If a metric does not have a result for a categorical variable, the result will be N/A.

    Args:
        - mann_d: dict with Mann-Whitney U-test results.
        - chi_d: dict with Chi-Squared test results.
        - table_style: Table style for the PDF.
        - num: Table numbering.
        - par_styles: Paragraph styles.
        - alpha: Significance level (default 0.05).

    Returns:
        A list of lists containing tables with statistical test results.
    """

    def format_p_values(p_values_dict, alpha):
        """Formats p-values, adding '*' if below significance threshold."""
        return [
            f"{round(p_value, 4)}*" if p_value < alpha else f"{round(p_value, 4)}"
            for p_value in p_values_dict.values()
        ]

    mann_whitney = {
        "Variables": list(mann_d.keys()),
        "p-values": format_p_values(mann_d, alpha),
    }
    chi_squared = {
        "Variables": list(chi_d.keys()),
        "p-values": format_p_values(chi_d, alpha),
    }

    pd1 = pd.DataFrame(mann_whitney)
    table_data1 = [pd1.columns.tolist()] + pd1.values.tolist()
    table_data1.insert(0, ["Mann Whitney U-test"])

    pd2 = pd.DataFrame(chi_squared)
    table_data2 = [pd2.columns.tolist()] + pd2.values.tolist()
    table_data2.insert(0, ["Chi Squared test"])

    t1 = Table(table_data1, style=table_style)
    p1 = Paragraph(f"Table {num}", style=par_styles["center_small"])
    num += 1
    t2 = Table(table_data2, style=table_style)
    p2 = Paragraph(f"Table {num}", style=par_styles["center_small"])
    num += 1

    return [[t1, t2], [p1, p2]]
