import copy

from rephorm.dict.styles import default_styles

class ChartPropertiesManager:
    def __init__(self):
        self.init_properties()

    def init_properties(self):

        # actually we don't need default here bcs it takes from styles in merge_settings anyway.
        self.default_bar_colors = default_styles()["chart"]["bar_color_order"]
        self.default_line_colors = default_styles()["chart"]["line_color_order"]
        self.default_line_styles = default_styles()["chart"]["line_styles_order"]
        self.default_line_widths = default_styles()["chart"]["line_width_order"]
        # set memory
        self.bar_colors = copy.deepcopy(self.default_bar_colors)
        self.line_widths = copy.deepcopy(self.default_line_widths)
        self.line_colors = copy.deepcopy(self.default_line_colors)
        self.line_styles = copy.deepcopy(self.default_line_styles)

        # set working stack
        self.bar_color_stack = copy.deepcopy(self.bar_colors)
        self.line_widths_stack = copy.deepcopy(self.line_widths)
        self.line_color_stack = copy.deepcopy(self.line_colors)
        self.line_style_stack = copy.deepcopy(self.line_styles)

    def get_bar_color(self):
        if not self.bar_color_stack:
            self.bar_color_stack = copy.deepcopy(self.bar_colors)
        return self.bar_color_stack.pop(0)

    def get_line_width(self):
        if not self.line_widths_stack:
            self.line_widths_stack = copy.deepcopy(self.line_widths)
        return self.line_widths_stack.pop(0)

    def get_line_color(self):
        if not self.line_color_stack:
            self.line_color_stack = copy.deepcopy(self.line_colors)
        return self.line_color_stack.pop(0)

    def get_line_style(self):
        if not self.line_style_stack:
            self.line_style_stack = copy.deepcopy(self.line_styles)
        return self.line_style_stack.pop(0)

    def update_colors_for_chart(self, bar_colors=None, line_colors=None, line_styles=None, line_widths=None):

        self.bar_color_stack.clear()
        self.line_color_stack.clear()
        self.line_style_stack.clear()
        self.line_widths_stack.clear()

        self.bar_colors = bar_colors if bar_colors and bar_colors is not None else copy.deepcopy(self.default_bar_colors)
        self.line_colors = line_colors if line_colors and line_colors is not None else copy.deepcopy(self.default_line_colors)
        self.line_styles = line_styles if line_styles and line_styles is not None else copy.deepcopy(self.default_line_styles)
        self.line_widths = line_widths if line_widths and line_widths is not None else copy.deepcopy(self.default_line_widths)

        self.bar_color_stack = copy.deepcopy(self.bar_colors)
        self.line_color_stack = copy.deepcopy(self.line_colors)
        self.line_style_stack = copy.deepcopy(self.line_styles)

chart_properties = ChartPropertiesManager()

def get_bar_color():
    return chart_properties.get_bar_color()

def get_line_width():
    return chart_properties.get_line_width()

def get_line_color():
    return chart_properties.get_line_color()


def get_line_style():
    return chart_properties.get_line_style()

def update_chart_properties(bar_colors=None, line_colors=None, line_styles=None, line_widths=None):
    return chart_properties.update_colors_for_chart(bar_colors, line_colors, line_styles, line_widths)