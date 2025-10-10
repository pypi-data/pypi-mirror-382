
class PageBreakMapper:
    def __init__(self, page_break):
        self.page_break = page_break

    def add_to_pdf(self, **kwargs):
        pdf = kwargs["pdf"]
        pdf.add_page()
