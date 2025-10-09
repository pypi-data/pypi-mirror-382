from logging import warning

from fpdf import FPDF

from rephorm.object_mappers._globals import get_figure_map
from rephorm.utility.report.cleanup_utility import perform_cleanup
from rephorm.utility.report.layout_utility import LayoutManager
from rephorm.utility.merge.pdf_merger import overlay_pdfs
from rephorm.utility.report.report_utility import set_title_page


class ReportMapper:

    def __init__(self, pdf: FPDF):
        self.pdf = pdf

    def compile(self, report, file_name: str, cleanup:bool = False):

        rs = report.settings.styles["report"]

        self.pdf.t_margin = rs["page_margin_top"]

        # TODO: Currently, we offset all bottom spacing to the bottom margin because FPDF2
        #  automatically breaks tables as soon as it reaches the bottom margin. This prevents
        #  any overlap with the footer, since the footer is included in fpdf.b_margin.
        #  We need to apply the same approach for the top margin and top spacing
        #  (e.g., header, title padding, etc.).
        # Also, make sure to verify whether any top padding or margin we have is actually
        # padding or margin. Padding refers to inner spacing, while margin is outer spacing.
        # Follow the standard convention.

        self.pdf.b_margin = rs["page_margin_bottom"] + rs["footer"]["height"] + rs["footer"]["top_margin"]
        self.pdf.l_margin = rs["page_margin_left"]
        self.pdf.r_margin = rs["page_margin_right"]
        self.pdf.c_margin = 0

        self.pdf.add_page()
        base_file_path = f"./tmp/report_tmp.pdf"
        directory_path = "./tmp/pdf_figures"

        used_top_height = rs["header"]["height"] + rs["header"]["bottom_margin"]

        layout_manager = LayoutManager(pdf=self.pdf, used_top_height=used_top_height)

        set_title_page(self.pdf, report)

        n_children = len(report.CHILDREN)

        for i, item in enumerate(report.CHILDREN):

            x, y, w, h = layout_manager.get_default_layout()
            mapper = item._get_mapper()
            # reset width to default
            # if children does not have width set by user, use the default width, if they do:
            # check if it does not exceed pdf.w and then use children's width instead.
            if hasattr(item, "width") and item.width is not None:
                if item.width > self.pdf.w:
                    warning(
                        f"{repr(item)} width: ({item.width}) | exceeds the PDF page width: ({self.pdf.w}). Falling back to defaults"
                    )
                else:
                    w = item.width

            mapper.add_to_pdf( pdf = self.pdf, w = w, h = h, x = x, y = y)

            if i < n_children-1:
                self.pdf.add_page()

        if not get_figure_map():
            self.pdf.output(f"{file_name}.pdf")
        else:
            self.pdf.output(base_file_path)
            overlay_pdfs(base_pdf_path=base_file_path, pdf_data=get_figure_map(),
                         output_pdf_path=f"{file_name}.pdf")
            perform_cleanup(cleanup, directory_path, base_file_path)

