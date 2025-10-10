from irispie import Series as IrisSeries

from rephorm.object_mappers.table_series_mapper import TableSeriesMapper
from rephorm.objects._utilities.settings_container import SettingsContainer
from rephorm.decorators.settings_validation import validate_kwargs
from rephorm.utility.add_style_prefix import add_prefix_to_styles


class TableSeries:

    @validate_kwargs
    def __init__(self, title: str = None, unit: str = None, data: IrisSeries = None, **kwargs):
        """
            :param data: (IrisSeries, Required) Data for the table series.
            :param title: (str) Name of the table series / row.
            :param unit: (str) The text value for the "units" column in this specific row of the table series.
            This defines what will be displayed as the unit for the corresponding row.
            :key span (ir.Span): Span of the table series.
            :key highlight (ir.Span): Span of the highlight in the table series.
            :key compare_style (str): Comparison style for the table series. "diff", "pct".
            :key decimal_precision (int): Sets number of decimal places after the decimal point.
            :key comparison_series (bool): Whether the series should be displayed as comparison series.
            :key styles (Dict): Styles dictionary for additional customization (for details refer to report object).
        """
        self.data = data
        self.title = title
        self.unit = unit
        self.settings = SettingsContainer(**kwargs)
        if hasattr(self.settings, "styles"):
            self.settings.styles = add_prefix_to_styles("table.series", self.settings.styles)

    def _get_mapper(self):
        return TableSeriesMapper(self)

    def __repr__(self):
        return f"{type(self).__name__}"