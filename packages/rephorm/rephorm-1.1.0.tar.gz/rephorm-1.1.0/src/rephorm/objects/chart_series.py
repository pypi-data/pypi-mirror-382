from irispie import Series as IrisSeries

from rephorm.object_mappers.chart_series_mapper import ChartSeriesMapper
from rephorm.objects._utilities.settings_container import SettingsContainer
from rephorm.decorators.settings_validation import validate_kwargs
from rephorm.utility.add_style_prefix import add_prefix_to_styles


class ChartSeries:

    @validate_kwargs
    def __init__( self, data: IrisSeries = None, **kwargs):
        """
            :param data (IrisSeries, Required): Data for the chart series.
            :key yaxis (str, Optional): Y-axis position for the chart series. Defaults to "left".
            :key span (ir.Span): Span of the chart series.
            :key show_legend (bool): to show/hide the legend for this data series.
            :key legend (tuple): Specifies the legend labels for the series. For a single series, use ("Label",).
            For multivariate series, provide multiple labels like ("Label 1", "Label 2", ...).
            :key highlight (ir.Span): Span of the highlight.
            :key series_type (str): Type of series to display - "line" for line charts, "bar" for bar charts,
            "bar_contribution" for contribution bar charts; use "line" with markers_mode="markers" for marker-based charts.
            :key markers_mode (str): Display style for data points - "lines+markers" (lines with symbols/dots),
            "lines" (lines only), or "markers" (symbols/dots only).
            :key marker_symbol (str): Symbol used for markers in the series. e.g., "asterisk".
            :key update_traces (Dict): Traces configuration for the chart series. (Plotly specific) todo: check if this is used
            :key styles (Dict): Styles dictionary for additional customization (for details refer to report object).
        """

        self.data = data
        self.settings = SettingsContainer(**kwargs)

        if hasattr(self.settings, "styles"):
            self.settings.styles = add_prefix_to_styles("chart.series", self.settings.styles)

    def _get_mapper(self):
        return ChartSeriesMapper(self)

    def __repr__(self):
        return f"{type(self).__name__}"