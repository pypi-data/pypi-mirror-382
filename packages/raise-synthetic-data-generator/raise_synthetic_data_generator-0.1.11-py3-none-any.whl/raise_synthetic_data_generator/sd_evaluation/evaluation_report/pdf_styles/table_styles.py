# -*- coding: utf-8 -*-
"""
    RAISE - RAI Synthetic Data Generator

    @author: Mikel Hernández Jiménez - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @author: Mikel Catalina Olazaguirre - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @version: 0.1
"""
# Stdlib imports

# Third-party app imports
from reportlab.platypus import TableStyle
from reportlab.lib import colors

# Imports from your apps


standard = TableStyle(
    [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("BACKGROUND", (0, 0), (-1, 0), "#0F172A"),
        ("GRID", (0, 1), (-1, -1), 0.5, "#0F172A"),
        ("GRID", (0, 0), (-1, 0), 0.5, colors.white),
    ]
)


left = TableStyle(
    [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("BACKGROUND", (0, 0), (0, -1), "#0F172A"),
        ("GRID", (0, 0), (-1, -1), 0.5, "#0F172A"),
    ]
)

types = TableStyle(
    [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 0), (-1, 0), "#0F172A"),
        ("GRID", (0, 1), (-1, -1), 0.5, "#0F172A"),
    ]
)

first_span = TableStyle(
    [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 0), (-1, 1), colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("BACKGROUND", (0, 0), (-1, 1), "#0F172A"),
        ("GRID", (0, 1), (-1, -1), 0.5, "#0F172A"),
        ("GRID", (0, 0), (-1, 1), 0.5, colors.white),
        ("SPAN", (0, 0), (1, 0)),
    ]
)

no_grid_table_style = TableStyle([("GRID", (0, 0), (-1, -1), 0, colors.white)])

top_aligned = TableStyle(
    [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]
)

styles = {
    "standard": standard,
    "left": left,
    "types": types,
    "span": first_span,
    "no_grid": no_grid_table_style,
    "top": top_aligned,
}


def get_table_styles(name):
    return styles[name]
