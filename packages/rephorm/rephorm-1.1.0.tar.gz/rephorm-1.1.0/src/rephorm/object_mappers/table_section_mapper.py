from fpdf import FontFace
from rephorm.utility.report.resolve_color import resolve_color

class TableSectionMapper:
    def __init__(self, table_section):
        self.table_section = table_section

    def add_to_pdf(self, **kwargs):

        n_cols = kwargs["n_cols"]
        highlight = kwargs["highlight"]
        pdf_table = kwargs["pdf_table"]
        span = kwargs["span"]
        title_row = pdf_table.row()


        for i in range(n_cols):

            color = resolve_color(self.table_section.settings.styles["table"]["section"]["highlight_color"])

            style = FontFace(
                emphasis= self.table_section.settings.styles["table"]["section"]["font_style"],
                size_pt=self.table_section.settings.styles["table"]["section"]["font_size"],
                fill_color= color if i in highlight else "#FFFFFF00",
                family=self.table_section.settings.styles["table"]["section"]["font_family"],
                color=self.table_section.settings.styles["table"]["section"]["font_color"],
            )

            content = self.table_section.TITLE if i == 0 else ""
            title_row.cell(content, style=style)

        for item in self.table_section.CHILDREN:
            mapper = item._get_mapper()
            mapper.add_to_pdf(span=span, pdf_table=pdf_table, highlight=highlight, show_units=self.table_section.settings.show_units)







