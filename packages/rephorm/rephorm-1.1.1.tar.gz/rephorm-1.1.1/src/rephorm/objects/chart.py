import copy
import plotly
from rephorm.object_mappers.chart_mapper import ChartMapper
from rephorm.objects.chart_series import ChartSeries
from rephorm.objects._utilities.settings_container import SettingsContainer
from rephorm.utility.add_style_prefix import add_prefix_to_styles

from rephorm.utility.report.range_utility import get_span, get_highlight
from rephorm.decorators.settings_validation import validate_kwargs

class Chart:

    @validate_kwargs
    def __init__(self, title: str = None, figure: plotly.graph_objs.Figure = None, **kwargs):
        """
            :args title (str): title of the chart
            :args figure (plotly.graph_objs.Figure): Plotly figure object. If provided, it will plot the given figure object.
            :args span (ir.Span): Span of the chart
            :key apply_report_layout (bool): If True, applies the standard report layout to the provided figure (can only be used for a custom Plotly figure).
            :key highlight (ir.Span): Span of the highlight.
            :key show_legend (bool): to show/hide the legend.
            :key show_grid (bool): to show/hide the grid.
            :key axis_border (bool): enable/disable axis borders.
            :key xaxis_title (str): The title for the X-axis.
            :key yaxis_title (str): The title for the Y-axis.
            :key yaxis2_title (str): The title for the second Y-axis.
            :key legend_orientation (str): legend orientation. "v" or "h".
            :key legend_position (str): Position of the legend. e.g. "SO" - South Outside. "S" - South Inside.
            :key series_type (str): Type of series to display - "line" for line charts, "bar" for bar charts,
            "bar_contribution" for contribution bar charts; use "line" with markers_mode="markers" for marker-based charts.
            :key markers_mode (str): Display style for data points - "lines+markers" (lines with symbols/dots),
            "lines" (lines only), or "markers" (symbols/dots only).
            :key legend (tuple): Specifies the legend labels for the series. For multivariate series, provide multiple labels like ("Label 1", "Label 2", ...).
            :key marker_symbol (str): Symbol name for markers, default is "asterisk".
            :key zeroline (bool): If True, displays a horizontal line at Y=0 to help indicate the zero baseline.
            :key styles (Dict): Styles dictionary for additional customization (for details refer to report object).
        """
        self.CHILDREN = []
        self.title = title
        self.figure = figure
        self.settings = SettingsContainer(**kwargs)

        if hasattr(self.settings, "styles"):
            self.settings.styles = add_prefix_to_styles("chart", self.settings.styles)

    def add(
            self,
            chart_child: ChartSeries = None):
        # Todo: add docstring later on.
        """
            :param chart_child: (ChartSeries) Child of the chart.
        """

        if chart_child is not None and isinstance(chart_child, ChartSeries):
            copy_chart_child = copy.deepcopy(chart_child)
            self.CHILDREN.append(copy_chart_child)

        else: raise Exception("CHART: Chart child of wrong type or None")

    def __repr__(self):
        return f"{type(self).__name__}"

    def _get_mapper(self):
        return ChartMapper(self)

    def _get_span(self):
        return get_span(self)

    def _get_highlight(self):
        return get_highlight(self)
