import copy
from typing import Optional, List, Union

from rephorm.objects.table_section import TableSection
from rephorm.objects.table_series import TableSeries
from rephorm.object_mappers.table_mapper import TableMapper
from rephorm.objects._utilities.settings_container import SettingsContainer
from rephorm.utility.add_style_prefix import add_prefix_to_styles
from rephorm.utility.report.range_utility import get_span, get_highlight
from rephorm.decorators.settings_validation import validate_kwargs
from rephorm.utility.report.table_utility import get_table_highlight


class Table:

    @validate_kwargs
    def __init__(self, title: str = "", footnotes: Optional[List[str]] = None, width: int = None, **kwargs):
        """
            :param title: Title of the table.
            :param footnotes: Footnotes for the title.
            :param width (int): The maximum width allowed for rendering the table.
            :key span (ir.Span, Required): Span of the table.
            :key highlight (ir.Span): Span of the highlight.
            :key show_units (bool): Display/hide units in the table.
            :key frequency (str): Frequency of the data in the table.
            :key decimal_precision (int): Sets number of decimal places after the decimal point.
            :key compare_style (str): Comparison style for the table series. "diff", "pct".
            :key layout (Dict): Layout configuration for the table (Plotly specific).
            :key styles (Dict): Styles dictionary for additional customization (for details refer to report object).
        """
        self.CHILDREN = []
        self.footnotes = footnotes
        self.title = title
        self.width = width
        self.settings = SettingsContainer(**kwargs)

        if hasattr(self.settings, "styles"):
            self.settings.styles = add_prefix_to_styles("table", self.settings.styles)


    def add(self, table_child: Union[TableSeries, TableSection] = None,):

        self._on_add_callback()

        if table_child is not None and isinstance(table_child, (TableSeries, TableSection)):
            copy_table_child = copy.deepcopy(table_child)
            self.CHILDREN.append(copy_table_child)
        else:
            raise Exception("Table: Table child of wrong type or None")

    def _get_mapper(self):
        return TableMapper(self)

    def _get_span(self):
        return get_span(self)

    def _get_highlight(self):
        return get_highlight(self)

    def _get_table_highlight(self):
        return get_table_highlight(self)

    # Because sometimes we may want to print the name of the object
    def __repr__(self):
        return f"{type(self).__name__}"

    def _on_add_callback(self):

        if hasattr(self.settings, 'styles'):
            highlight_color = self.settings.styles.get("table.highlight_color")

            if highlight_color:
                # Set default values for various highlight_color properties
                self.settings.styles.setdefault("table.series.highlight_color", highlight_color)
                self.settings.styles.setdefault("table.heading.highlight_color", highlight_color)
                self.settings.styles.setdefault("table.section.highlight_color", highlight_color)
