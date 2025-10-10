import copy

from rephorm.object_mappers.table_section_mapper import TableSectionMapper
from rephorm.objects.table_series import TableSeries
from rephorm.objects._utilities.settings_container import SettingsContainer
from rephorm.decorators.settings_validation import validate_kwargs
from rephorm.utility.add_style_prefix import add_prefix_to_styles


class TableSection:

    @validate_kwargs
    def __init__(self, title: str = None, **kwargs):
        """
            :param title: (str) Title of the table section.
            :key styles (Dict): Styles dictionary for the table section (refer to documentation).
            :key highlight (ir.Span): Span of the highlight in the table section. (applies to all table_series added within the section)
            :key show_units (bool): To show/hide units for the table section. (applies to all table_series added within the section)
        """
        self.TITLE = title
        self.CHILDREN = []
        self.settings = SettingsContainer(**kwargs)
        if hasattr(self.settings, "styles"):
            self.settings.styles = add_prefix_to_styles("table.section", self.settings.styles)

    def add (self, table_section_child: TableSeries = None):

        self._on_add_callback()

        if table_section_child is not None and isinstance(table_section_child, TableSeries):
            copy_table_section_child = copy.deepcopy(table_section_child)
            self.CHILDREN.append(copy_table_section_child)
        else:
            raise Exception("TableSection: Table Section child of wrong type or None")

    def _get_mapper(self):
        return TableSectionMapper(self)

    def __repr__(self):
        return f"{type(self).__name__}"

    def _on_add_callback(self):
        if hasattr(self.settings, 'styles'):
            highlight_color = self.settings.styles.get("table.section.highlight_color")
            if highlight_color:
                self.settings.styles.setdefault("table.series.highlight_color", highlight_color)
                self.settings.styles.setdefault("table.section.highlight_color", highlight_color)

