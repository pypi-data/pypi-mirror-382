import os

import irispie
import numpy as np
from plotly.graph_objects import Figure

from rephorm.object_mappers._globals import set_figure_map
from rephorm.object_mappers._utilities.chart_mapper_utility import process_bar_data
from rephorm.utility.report.image_utility import to_image
from rephorm.dict.update_layout import update_layout
from rephorm.utility.report.resolve_color import resolve_highlight_color


class ChartMapper:

    def __init__(self, chart):
        self.chart = chart
        self.figure = Figure()
        self.apply_report_layout = chart.settings.apply_report_layout

    def add_to_pdf(self, **kwargs):
        grid_size = kwargs.get("grid_size", 1)
        pdf = kwargs["pdf"]
        x = kwargs["x"]
        y = kwargs["y"]
        w = kwargs["w"]
        h = kwargs["h"]

        scale_f = pdf.k

        img_w = w * scale_f
        img_h = h * scale_f

        if grid_size > 9:
            img_w = None
            img_h = None

        # Todo: Directory creation and check, should be extracted from here, too many concerns...
        directory = "./tmp/pdf_figures"
        os.makedirs(directory, exist_ok=True)

        self.figure = self.chart.figure or self._add_internal_figure()

        if self.apply_report_layout and bool(self.chart.figure):
            update_layout(self.chart.figure.layout.title.text, self.chart.settings, self.figure)

        data = to_image(self.figure, image_format="pdf", width=img_w, height=img_h)

        if data is None:
            raise ValueError(f"ChartMapper: Failed to render chart image. Data is: {data}")

        file_path = f"{directory}/{id(self.chart)}.pdf"
        with open(file_path, "wb") as f:
            f.write(data)

        fig_map = ({"page": pdf.page_no(),
                    "pdf_path": file_path,
                    "x": x * scale_f,
                    "y": y * scale_f,
                    "width": w * scale_f,
                    "height": h * scale_f})

        set_figure_map(fig_map)

    def _add_internal_figure(self):

        min_y = None
        max_y = None

        span = self.chart._get_span()
        span_length = len(span)
        neg_stacked_bars_data = np.zeros(span_length)
        pos_stacked_bars_data = np.zeros(span_length)
        stacked_bars = False

        for item in self.chart.CHILDREN:
            for variant in range(1, item.data.num_variants + 1):
                y_values = item.data.get_data_variant_from_until(span, variant).flatten()
                if item.settings.series_type in ("barcon", "conbar", "contribution_bar", "bar_relative"):
                    stacked_bars = True
                    neg_stacked_bars_data, pos_stacked_bars_data = process_bar_data(
                        neg_stacked_bars_data,
                        pos_stacked_bars_data,
                        y_values
                    )
                else:
                    # Direct min/max calculation for non-barcon series
                    current_min = y_values.min()
                    current_max = y_values.max()

                    min_y = current_min if min_y is None else min(min_y, current_min)
                    max_y = current_max if max_y is None else max(max_y, current_max)

            series_mapper = item._get_mapper()
            series_mapper.add_to_pdf(
                figure=self.figure)  # Todo: This add_to_pdf call is confusing, yes, we wanted to unify function names, but in this case it does not make sense.

        if stacked_bars:
            min_y = min(neg_stacked_bars_data) if min_y is None else min(min_y, min(neg_stacked_bars_data))
            max_y = max(pos_stacked_bars_data) if max_y is None else max(max_y, max(pos_stacked_bars_data))

        dy = max_y - min_y
        y_range = [min_y - dy * 0.01, max_y + dy * 0.01]

        update_layout(self.chart.title, self.chart.settings, self.figure, y_range)

        # Adjusts view SPAN on charts. "Slices" any padding between.
        # self.figure.layout.xaxis.range = [span.start.to_python_date(position="start"),
        #                                   span.end.to_python_date(position="end")]

        if self.chart.settings.highlight is not None:
            irispie.plotly.highlight(self.figure, self.chart._get_highlight(),
                                     color=resolve_highlight_color(
                                         self.chart.settings.styles["chart"]["highlight_color"], alpha=0.25))

            # Todo: This is a workaround for the issue with the highlight. It should be fixed in the irispie library.
            #  therefore, delete update_shapes() call here, when it's fixed in iris-pie
            self.figure.update_shapes({"layer": "below"})

        return self.figure
