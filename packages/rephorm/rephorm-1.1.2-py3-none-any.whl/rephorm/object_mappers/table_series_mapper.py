
from fpdf import FontFace

from rephorm.utility.report.resolve_color import resolve_color
from rephorm.utility.report.table_utility import prepare_row


class TableSeriesMapper:
    def __init__(self, series):
        self.series = series

    def add_to_pdf(self, **kwargs):


        highlight = kwargs["highlight"]
        pdf_table = kwargs["pdf_table"]
        span = kwargs["span"]
        show_units = kwargs["show_units"]
        #fpdf = kwargs["fpdf"]#todo: add to kwargs
        # last_y = kwargs["footer_last_y"] # We get last Y from parent,
        # so to add footnote to the bottom of the page right after parent footnotes.

        # Get start page nr before adding row
        # start_page_nr = fpdf.page_no()

        # add row
        element_row = pdf_table.row()

        #get page number after adding row
        # current_page_nr = fpdf.page_no()

        # In case the first element is on the next page, we need to reset last_y to none,
        # so that the add_footnotes_at_bottom function recalculates footnote positions
        # if current_page_nr > start_page_nr:
        #     last_y = None

        #Gen references here, pass it down to prep row and later to add_footnotes_. ...
        # footnote_references = generate_footnote_numbers(self.series.footnotes)

        row = prepare_row(
            series=self.series,
            compare_style=self.series.settings.compare_style,
            span=span,
            show_units=show_units,
            unit=self.series.unit,
            title=self.series.title,
            decimal_precision=self.series.settings.decimal_precision,
            footnote_references=None, # Todo: footnote_references
        )

        # add_footnotes_at_bottom(footnotes=self.series.footnotes,
        #     last_y=last_y,)

        color = resolve_color(self.series.settings.styles["table"]["series"]["highlight_color"])

        # I think we use similar logic in couple places, look if it's the case and put in utility.
        for i, cell in enumerate(row):  # Process each cell in the row

            style = FontFace(
                family=self.series.settings.styles["table"]["series"]["font_family"],
                emphasis=self.series.settings.styles["table"]["series"]["font_style"],
                size_pt=self.series.settings.styles["table"]["series"]["font_size"],
                fill_color= color if i in highlight else "#FFFFFF00",
                color=resolve_color(self.series.settings.styles["table"]["series"]["font_color"]),
            )

            # ^^^^^^^^^^^^^^^^^^^^^^^^^^

            if self.series.settings.comparison_series:
                padding = (-self.series.settings.styles["table"]["series"]["font_size"]*0.6, 0, 5, 0)
                style.size_pt *= 0.8 # Sets size of comparison series
            else:
                padding = (0, 0, 0, 0)

            element_row.cell(
                cell,
                style=style,
                padding = padding,
            )
