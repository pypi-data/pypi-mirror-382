import copy
from typing import Optional, Dict, Text, Union

from rephorm.objects.grid import Grid
from rephorm.objects.table import Table
from rephorm.objects.text import Text
from rephorm.objects.page_break import PageBreak
from rephorm.objects.chart import Chart
from rephorm.objects.chapter import Chapter

from rephorm.objects._utilities.settings_container import SettingsContainer
from rephorm.utility.add_style_prefix import add_prefix_to_styles
from rephorm.utility.fonts.font_loading import get_fonts, add_custom_fonts
from rephorm.object_mappers.report_mapper import ReportMapper
from rephorm.utility.PDF import PDF
from rephorm.utility.merge.merge_settings import merge_settings
from rephorm.decorators.settings_validation import validate_kwargs


class Report:
    @validate_kwargs
    # Todo: delete report name from here, it is not needed since you can specify it on output method call
    def __init__(self, title: str = "", subtitle: str = "", load_fonts: Optional[list[Dict[str, str]]] = None, abstract: str="", **kwargs):
        # Todo: consider moving `load_fonts` to `kwargs` (Currently, it would be hard to validate entry/value if we move to kwargs, bcs of it's complex value type)
        # Todo: add new setting `show_title_page=True` to control whether to create the front page or not (and make sure the header creation is aware of this parameter)
        """
            **Params:**
                - ``title`` (str): Title of the report. Placed in the front page.
                - ``subtitle`` (str): Subtitle of the report. Placed in the front page after the title.
                - ``load_fonts`` (list[Dict[str, str]]): Fonts to load for the report.
                 For ``load_fonts`` you need to specify font_family, font_style and font_path as dictionary.

            **Kwargs:**
                - ``orientation`` (str): Orientation of the report, e.g., 'P' for Portrait, 'L' for Landscape.
                - ``unit`` (str): Measurement unit for the report, e.g., 'pt', 'mm', 'cm'.
                - ``format`` (str): Paper format for the report, e.g., 'A4', 'Letter'.
                - ``logo`` (str): Path to the logo file for the report.
                - ``styles`` (Dict): Styles dictionary for additional customization. See below for keys.

            **Styles Dictionary Keys:**

            **Table**
                *title*
                    - ``table.title.font_style`` (str)
                    - ``table.title.font_family`` (str)
                    - ``table.title.font_color`` (str)
                    - ``table.title.font_size`` (float)

                *heading*
                    - ``table.heading.font_style`` (str)
                    - ``table.heading.font_family`` (str)
                    - ``table.heading.font_color`` (str)
                    - ``table.heading.font_size`` (float)
                    - ``table.heading.highlight_color`` (str): color name

                *series*
                    - ``table.series.font_style`` (str)
                    - ``table.series.font_family`` (str)
                    - ``table.series.font_color`` (str)
                    - ``table.series.font_size`` (float)
                    - ``table.series.highlight_color`` (str): color name

                **section**
                    - ``table.section.font_family`` (str)
                    - ``table.section.font_color`` (str)
                    - ``table.section.font_size`` (float)
                    - ``table.section.highlight_color`` (str): color name

            **Chart:**
                **general**
                    - ``chart.highlight_color`` (str)
                    - ``chart.grid_color`` (str)
                    - ``chart.bg_color`` (str): Background color of the chart.
                    - ``chart.chart_border_color`` (str): Border color of the chart. If border is applied
                **legend**
                    - ``chart.legend.border_width`` (int):
                    - ``chart.legend.bg_color`` (str):
                    - ``chart.legend.font_style`` (str):
                    - ``chart.legend.font_family`` (str):
                    - ``chart.legend.font_color`` (str):
                    - ``chart.legend.font_size`` (float):

                **title**
                    - ``chart.title.font_style`` (str)
                    - ``chart.title.font_family`` (str)
                    - ``chart.title.font_color`` (str)
                    - ``chart.title.font_size`` (float)

                **x_axis:**
                    *ticks:*
                        - ``chart.x_axis.ticks.font_size`` (float)
                        - ``chart.x_axis.ticks.font_color`` (str)
                        - ``chart.x_axis.ticks.font_family`` (str)
                    *label:*
                        - ``chart.x_axis.label.font_size`` (float)
                        - ``chart.x_axis.label.font_color`` (str)
                        - ``chart.x_axis.label.font_family`` (str)

                **y_axis:**
                    *ticks:*
                        - ``chart.y_axis.ticks.font_size`` (float)
                        - ``chart.y_axis.ticks.font_color`` (str)
                        - ``chart.y_axis.ticks.font_family`` (str)
                    *label:*
                        - ``chart.y_axis.label.font_size`` (float)
                        - ``chart.y_axis.label.font_color`` (str)
                        - ``chart.y_axis.label.font_family`` (str)

                **series:**
                    - ``chart.series.bar_edge_color`` (str): Border color for bars in bar charts, default black.
                    - ``chart.series.bar_edge_width`` (int): Border width for bars in bar charts.
                    - ``chart.series.bar_face_color`` (str): Fill color for bars in bar charts, default green.
                    - ``chart.series.line_width`` (int): Line width, default 1.
                    - ``chart.series.line_style`` (str): 'solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot'.
                    - ``chart.series.line_color`` (str): Color of the line.
                    - ``chart.series.marker_color`` (str): Color of the marker symbol.
                    - ``chart.series.marker_size`` (int): Size of the marker symbol.
                    - ``chart.series.marker_width`` (int): Marker width default is 0; some, like asterisks, require a width of 1.

            **Report:**
                - ``report.font_style`` (str)
                - ``report.font_family`` (str)
                - ``report.font_color`` (str)
                - ``report.font_size`` (float)
                - ``report.page_margin_left`` (int)
                - ``report.page_margin_top`` (int)

            **Text:**
                - ``text.font_style`` (str): as string: "B", "I", "BI"
                - ``text.font_family`` (str)
                - ``text.font_size`` (float)

            **Chapter:**
                - ``chapter.font_style`` (str)
                - ``chapter.font_family`` (str)
                - ``chapter.font_size`` (float)

            :key kwargs (any): You can provide any key-value pair to customize settings. If Object A contains Object B, settings for Object B can be defined in Object A and will apply to all instances of Object B, unless overridden for a specific instance
        """

        self.CHILDREN = []
        self.title = title
        self.subtitle = subtitle
        self.load_fonts = get_fonts(load_fonts)
        self.abstract = abstract
        self.settings = SettingsContainer(**kwargs)

        if hasattr(self.settings, "styles"):
            self.settings.styles = add_prefix_to_styles("report", self.settings.styles)

        merge_settings(self, self.settings.__dict__)

    def add(self, report_child : Union[Grid, Table, Text, PageBreak, Chart, Chapter] = None):
        if report_child is not None and isinstance(report_child, (Grid, Table, Text, PageBreak, Chart, Chapter)):
            copy_report_child = copy.deepcopy(report_child)
            self.CHILDREN.append(copy_report_child)
            merge_settings(self, self.settings.__dict__)
        else: raise Exception("Report: report child of wrong type or None")

    # TODO: Output needs to know about mapper, so regarding circularity, extracting output would help us.
    # Should be part of report mapper
    def output(self, file_name: str = "report", cleanup: bool = True):
        """
            :args file_name (str): name of the report output file
            :args cleanup (bool): if True, figures will be kept within /tmp directory
        """

        pdf = PDF(
            orientation = self.settings.orientation,
            unit = self.settings.unit,
            format = self.settings.format,
            report_styles=self.settings.styles["report"],
            report_title=self.title,
        )

        add_custom_fonts(pdf, self.load_fonts)

        pdf.set_margins(left=self.settings.styles["report"]["page_margin_left"],
                         top=self.settings.styles["report"]["page_margin_top"])

        reportMapper = ReportMapper(pdf)

        reportMapper.compile(self, file_name, cleanup)

    def set_front_page(self, title: str = "", subtitle: str = "", abstract: str="", logo: Optional[str] = None):
        if bool(title):
            self.title = title
        if bool(subtitle):
            self.subtitle = subtitle
        if bool(abstract):
            self.abstract = abstract
        if bool(logo):
            self.settings.logo = logo



