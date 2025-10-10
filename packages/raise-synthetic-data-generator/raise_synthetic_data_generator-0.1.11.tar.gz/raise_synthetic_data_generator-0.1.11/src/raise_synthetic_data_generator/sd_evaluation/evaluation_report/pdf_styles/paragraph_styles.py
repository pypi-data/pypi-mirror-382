# -*- coding: utf-8 -*-
"""
    RAISE - RAI Synthetic Data Generator

    @author: Mikel Hernández Jiménez - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @author: Mikel Catalina Olazaguirre - Vicomtech Foundation, Basque Research and Technology Alliance (BRTA)
    @version: 0.1
"""
# Stdlib imports

# Third-party app imports
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER

# Imports from your apps

title = ParagraphStyle(
    name="Title",
    fontName="Times-Bold",
    fontSize=18,
    leading=22,
    alignment=TA_CENTER,
    spaceAfter=8,
)


h1 = ParagraphStyle(name="Heading1", fontName="Times-Bold", fontSize=18, leading=22)

h2 = ParagraphStyle(
    name="Heading2",
    fontName="Times-Bold",
    fontSize=16,
    leading=22,
    spaceBefore=10,
    spaceAfter=10,
)

h3 = ParagraphStyle(
    name="Heading3",
    fontName="Times-Bold",
    fontSize=14,
    leading=22,
)

h4 = ParagraphStyle(name="Heading4", fontName="Times-Bold", fontSize=12, leading=22)

h5 = ParagraphStyle(name="Heading5", fontName="Times-Bold", fontSize=11, leading=22)

h6 = ParagraphStyle(
    name="Heading6", fontName="Times-Bold", fontSize=7, leading=8.4, spaceBefore=6
)

normal = ParagraphStyle(
    name="Normal", fontName="Times-Roman", fontSize=10, leading=12, alignment=TA_JUSTIFY
)

bullet = ParagraphStyle(
    name="Bullet",
    alignment=TA_JUSTIFY,
    allowOrphans=0,
    allowWidows=1,
    backColor=None,
    borderColor=None,
    borderPadding=0,
    borderRadius=None,
    borderWidth=0,
    bulletAnchor="start",
    bulletFontName="Symbol",
    bulletFontSize=10,
    bulletIndent=18,
    embeddedHyphenation=1,
    endDots=None,
    firstLineIndent=0,
    fontName="Times-Roman",
    fontSize=10,
    hyphenationLang="en_GB",
    justifyBreaks=0,
    justifyLastLine=0,
    leading=12,
    leftIndent=54,
    linkUnderline=0,
    rightIndent=0,
    spaceAfter=0,
    spaceBefore=0,
    spaceShrinkage=0.05,
    splitLongWords=1,
    textTransform=None,
    underlineColor=None,
    uriWasteReduce=0.3,
    wordWrap=None,
)


centered_small = ParagraphStyle(
    name="Center_small",
    fontName="Helvetica",
    leftIndent=0,
    fontSize=8,
    alignment=TA_CENTER,
)

left_small = ParagraphStyle(
    name="Center_small",
    fontName="Helvetica",
    leftIndent=0,
    fontSize=8,
    alignment=TA_LEFT,
)


toc = [
    ParagraphStyle(
        fontName="Times-Bold",
        fontSize=14,
        name="TOCHeading1",
        leftIndent=20,
        firstLineIndent=-20,
        spaceBefore=5,
        leading=16,
    ),
    ParagraphStyle(
        fontName="Times-Roman",
        fontSize=12,
        name="TOCHeading2",
        leftIndent=40,
        firstLineIndent=-20,
        spaceBefore=0,
        leading=12,
    ),
    ParagraphStyle(
        fontName="Times-Roman",
        fontSize=10,
        name="TOCHeading3",
        leftIndent=60,
        firstLineIndent=-20,
        spaceBefore=0,
        leading=12,
    ),
    ParagraphStyle(
        fontName="Times-Roman",
        fontSize=10,
        name="TOCHeading4",
        leftIndent=100,
        firstLineIndent=-20,
        spaceBefore=0,
        leading=12,
    ),
]

styles = {
    "title": title,
    "h1": h1,
    "h2": h2,
    "h3": h3,
    "h4": h4,
    "h5": h5,
    "h6": h6,
    "normal": normal,
    "center_small": centered_small,
    "left_small": left_small,
    "toc": toc,
    "bullet": bullet,
}


def get_paragraph_styles():
    return styles
