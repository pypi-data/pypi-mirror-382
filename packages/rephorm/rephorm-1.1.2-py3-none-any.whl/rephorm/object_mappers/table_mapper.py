from fpdf import FontFace

from rephorm.object_mappers._utilities.table_mapper_utility import (
    get_max_numerical_width,
    get_max_width,
)
from rephorm.utility.report.add_footnotes import add_footnotes_at_bottom
from rephorm.utility.report.footnotes_counter import generate_footnote_numbers
from rephorm.utility.report.report_utility import get_page_dimensions
from rephorm.utility.report.resolve_color import resolve_color
from rephorm.utility.report.title_utility import add_title_with_references


class TableMapper:
    def __init__(self, table):
        self.table = table

    def add_to_pdf(self, **kwargs):

        pdf = kwargs["pdf"]
        highlight = []
        x = kwargs["x"]
        w = kwargs["w"]
        h = kwargs["h"]
        y = kwargs["y"]

        title_bottom_padding = self.table.settings.styles["report"]["title_bottom_padding"]
        #Todo: Consider extracting context based on caller. So we do not need to deal with string checks. Discuss with Sergey.
        context = kwargs.get("context", None)
        custom_width = self.table.width
        footer_top_padding = self.table.settings.styles["report"]["footer"]["top_padding"]
        footer_top_margin = self.table.settings.styles["report"]["footer"]["top_margin"]
        footer_last_y = kwargs["footer_last_y"] if "footer_last_y" in kwargs else None

        # Todo: Consider replacing (full_width_grid) conditional based on grid row settings? if nrow and ncol = 1? Talk to Sergey why
        full_width_grid = (w == pdf.epw)
        is_multi_cell_grid = context == "grid" and not full_width_grid

        skip_cols = 1
        headers = [""]

        pdf.set_xy(x, y)
        page_width, _ = get_page_dimensions(pdf)

        num_col_width = get_max_numerical_width(
            self.table,
            pdf,
            font_family=self.table.settings.styles["table"]["series"]["font_family"],
            font_size=self.table.settings.styles["table"]["series"]["font_size"],
            biggest_nr="10000",
        )

        title_col_width = get_max_width(
            self.table,
            pdf,
            font_family=self.table.settings.styles["table"]["series"]["font_family"],
            font_size=self.table.settings.styles["table"]["series"]["font_size"],
            parameter="title",
            max_width=0,
        )
        unit_col_width = get_max_width(
            self.table,
            pdf,
            font_family=self.table.settings.styles["table"]["series"]["font_family"],
            font_size=self.table.settings.styles["table"]["series"]["font_size"],
            parameter="unit",
            max_width=0,
        )

        if self.table.settings.highlight is not None:
            highlight = self.table._get_table_highlight()

        span = self.table._get_span()

        if self.table.settings.show_units:
            skip_cols += 1

        if self.table.settings.show_units:
            headers = headers + ["Units"]

        heading_data = [
            headers + list(span.to_compact_strings()),
        ]

        heading = heading_data[0][skip_cols:]

        num_col_padding = 10

        col_widths = (
            [
                title_col_width + 10
            ]  # TODO: first column width | We introduce param for this. the name of param: title_col_width
            + [unit_col_width + 0]
            * self.table.settings.show_units  # TODO: second column width | We introduce param for this. the name of param: unit_col_width
            + [num_col_width + num_col_padding] * len(heading)  # numerical columns width
        )

        # we use effective page width here (excluding margins)
        page_width = pdf.epw

        natural_table_width = sum(col_widths) + 10

        if natural_table_width > page_width:
            table_width = page_width
        else:
            if is_multi_cell_grid:
                table_width = w
            else:
                table_width = natural_table_width

        text_align = ["L"] * skip_cols + ["R"] * len(heading)

        h_data = headers + heading

        # ----------------- Set Table Title -----------------

        footnote_references = generate_footnote_numbers(self.table.footnotes)
        y = add_title_with_references(
            pdf=pdf,
            title=self.table.title,
            references=footnote_references,
            font_family=self.table.settings.styles["table"]["title"]["font_family"],
            font_size=self.table.settings.styles["table"]["title"]["font_size"],
            font_style=self.table.settings.styles["table"]["title"]["font_style"],
            title_y=y,
            cell_width=w,
        )
        if bool(self.table.footnotes):
            footer_last_y = add_footnotes_at_bottom(
                pdf,
                self.table.footnotes,
                footnote_references,
                last_y=footer_last_y,
                font_family=self.table.settings.styles["footnotes"]["font_family"],
                font_size=self.table.settings.styles["footnotes"]["font_size"],
                font_style=self.table.settings.styles["footnotes"]["font_style"],
                footer_padding=footer_top_padding,
                footer_top_margin=footer_top_margin,
            )

        # Todo: Consider: title padding could be part of add_title_with_ref function, so we only pass here Y after calling that func)
        pdf.set_y(y + title_bottom_padding)

        # ----------------- Set Table Header -----------------
        with pdf.table(
            width=custom_width if custom_width else table_width,
            col_widths=col_widths,
            text_align=text_align,
            align="l" if is_multi_cell_grid else "c",
            # TODO: ADD border settings to styles for table
            borders_layout="SINGLE_TOP_LINE",
            # line height sets the height of rows, 1,4 is multiplier. (We cannot precisely extract height of the text)
            # Todo: Consider extracting this to param/styles, like inrow_offset...
            line_height=self.table.settings.styles["table"]["series"]["font_size"]
            * 1.4,
        ) as pdf_table:

            heading_row = pdf_table.row()
            header_color = resolve_color(
                self.table.settings.styles["table"]["heading"]["highlight_color"]
            )

            for i, header in enumerate(h_data):
                # Todo: Remove Grey and etc params from table object and move them to styles
                style = FontFace(
                    emphasis=self.table.settings.styles["table"]["heading"][
                        "font_style"
                    ],
                    size_pt=self.table.settings.styles["table"]["heading"]["font_size"],
                    fill_color=header_color if i in highlight else "#FFFFFF00",
                    family=self.table.settings.styles["table"]["heading"][
                        "font_family"
                    ],
                    color=resolve_color(
                        self.table.settings.styles["table"]["heading"]["font_color"]
                    ),
                )

                heading_row.cell(header, style=style)

            # ----------------- Set Table Rows -----------------
            for item in self.table.CHILDREN:
                mapper = item._get_mapper()
                mapper.add_to_pdf(
                    span=span,
                    pdf_table=pdf_table,
                    highlight=highlight,
                    n_cols=len(col_widths),
                    show_units=self.table.settings.show_units,
                    footer_last_y=footer_last_y,
                )
