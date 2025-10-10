from datetime import datetime

from fpdf import FPDF

"""
This subclass extends FPDF to include customized header and footer functionality,
making it easier to apply consistent formatting across all pages of the document.
By overriding the `header` and `footer` methods, we ensure that these elements
are automatically added to each page without manual intervention.
"""

class PDF(FPDF):
    def __init__(self, report_styles = None, report_title = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.report_styles = report_styles
        self.report_title = report_title
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def header(self):
        header_height = self.report_styles["header"]["height"]
        self.set_font(family=self.report_styles["font_family"], size=8)
        # Todo: here, H should be set to header height
        # Set absolute position for the header
        # We need to skip first cell (bcs of logo).
        header_width = self.epw / 3
        y = self.get_y()

        layout = self._get_header_layout(self.page_no(), self.timestamp, self.report_title)

        for item in layout:
            x = self.l_margin + item["slot"] * header_width
            self.set_xy(x, y)
            self.cell(
                w=header_width,
                h=header_height,
                text=item["text"],
                align=item.get("align", "L"),
                # border=1 #for debugging
            )
    # Todo: was easier to extract it like this, and in the future we could rewr this function
    #  further in order to specify exact positions of elements.
    def _get_header_layout(self, page_no, timestamp, report_title):
        layout = [
            {
                "id": "title",
                "text": report_title,
                "align": "L",
                "slot": 0
            },
            {
                "id": "page",
                "text": f"Page {page_no}",
                "align": "C",
                "slot": 1
            },
            {
                "id": "timestamp",
                "text": timestamp,
                "align": "R",
                "slot": 2
            }
        ]

        # Todo: modify this, once we have show_title_page option on report object that controls whether the
        #  title page shown or not.
        if page_no == 1:
            layout = [{
                "id": "timestamp",
                "text": timestamp,
                "align": "R",
                "slot": 2
            }]

        return layout






