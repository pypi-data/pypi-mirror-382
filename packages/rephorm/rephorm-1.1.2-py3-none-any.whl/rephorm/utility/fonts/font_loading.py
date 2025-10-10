import os
import sys
from logging import warning


def get_fonts(load_fonts):

    default_fonts = get_default_fonts()

    if not load_fonts:
        return default_fonts

    font_map = {(font['font_path']): font for font in default_fonts}

    # Update or append additional fonts
    for font in load_fonts:
        key = (font['font_path'])
        font_map[key] = font

    return list(font_map.values())

def get_default_fonts():
    base_path = os.path.abspath(os.path.dirname(__file__))
    return [
        {
         "font_family": "Open Sans",
         "font_path": os.path.join(base_path, "OpenSans.ttf"),
         "font_style": ""},
        {
         "font_family": "Open Sans",
         "font_path": os.path.join(base_path, "OpenSans-Italic.ttf"),
         "font_style": "I"},
        {
         "font_family": "Open Sans",
         "font_path": os.path.join(base_path, "OpenSans-Bold.ttf"),
         "font_style": "B"},
        {
         "font_family": "Open Sans",
         "font_path": os.path.join(base_path, "OpenSans-BoldItalic.ttf"),
         "font_style": "BI"},
    ]

def validate_fonts(fonts):

    required_styles = {"", "I", "B"}

    grouped_fonts = {}
    for font in fonts:
        family = font["font_family"]
        style = font["font_style"].upper()
        if family not in grouped_fonts:
            grouped_fonts[family] = set()
        grouped_fonts[family].add(style)

    for font_family, available_styles in grouped_fonts.items():
        missing_styles = required_styles - available_styles
        if missing_styles:
            raise Exception(f"Font family '{font_family}' is missing styles: {', '.join(missing_styles)}")


def add_custom_fonts(pdf, fonts):

    if fonts is not None:
        try:
            validate_fonts(fonts)
        except Exception as e:
            warning(e)
            sys.exit(1)

            # Font loading
    for font_dict in fonts:
        pdf.add_font(family = font_dict.get("font_family"),
                     fname=font_dict.get('font_path'),
                     style=font_dict.get('font_style', ''))
