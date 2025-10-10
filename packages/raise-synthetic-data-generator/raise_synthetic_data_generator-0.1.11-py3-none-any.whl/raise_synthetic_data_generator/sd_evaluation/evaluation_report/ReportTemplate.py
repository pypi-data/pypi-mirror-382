from reportlab.platypus import BaseDocTemplate


class ReportTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kw)

    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if flowable.__class__.__name__ == "Paragraph":
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == "Heading1":
                key = "h1-%s" % self.seq.nextf("heading1")
                self.canv.bookmarkPage(key)
                self.notify("TOCEntry", (0, text, self.page, key))
            if style == "Heading2":
                key = "h2-%s" % self.seq.nextf("heading2")
                self.canv.bookmarkPage(key)
                self.notify("TOCEntry", (1, text, self.page, key))
            if style == "Heading3":
                key = "h3-%s" % self.seq.nextf("heading3")
                self.canv.bookmarkPage(key)
                self.notify("TOCEntry", (2, text, self.page, key))
            if style == "Heading4":
                key = "h4-%s" % self.seq.nextf("heading4")
                self.canv.bookmarkPage(key)
                self.notify("TOCEntry", (3, text, self.page, key))
            if style == "Heading5":
                key = "h5-%s" % self.seq.nextf("heading5")
                self.canv.bookmarkPage(key)
                self.notify("TOCEntry", (4, text, self.page, key))
