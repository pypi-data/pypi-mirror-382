from rephorm.dict.update_traces import update_base_traces, apply_per_trace_styles


class ChartSeriesMapper:
    def __init__(self, series):
        self.series = series

    def add_to_pdf(self, **kwargs):

        figure = kwargs["figure"]
        num_variants = self.series.data.num_variants
        # Here we will get either single value or a list of values, depends if multivariate or not:
        line_colors = self.series.settings.styles["chart"]["series"]["line_color"]
        line_widths = self.series.settings.styles["chart"]["series"]["line_width"]
        line_styles = self.series.settings.styles["chart"]["series"]["line_style"]
        bar_colors = self.series.settings.styles["chart"]["series"]["bar_face_color"]

        def get_series_type(key):
            mapping = {
                "line": "line",
                "bar": "bar",
                "bar_stack": "bar_stack",
                "contribution_bar": "bar_relative",
                "conbar": "bar_relative",
                "barcon": "bar_relative",
                "bar_relative": "bar_relative",
                "bar_group": "bar_group",
                "bar_overlay": "bar_overlay",
            }
            return mapping.get(key)

        fig = self.series.data.plot(
            span=self.series.settings.span,
            date_format_style="compact",
            date_axis_mode="instant",
            figure=figure,
            chart_type=get_series_type(self.series.settings.series_type),
            legend=self.series.settings.legend,
            show_legend=self.series.settings.show_legend,
            return_info=True,
            show_figure=False,
            update_traces=update_base_traces(self.series.settings)
        )

        apply_per_trace_styles(
            fig["figure"],
            line_colors,
            line_widths,
            line_styles,
            bar_colors,
            num_variants,
        )