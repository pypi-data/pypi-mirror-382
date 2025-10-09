#TODO: extract this function to external module.
from typing import Literal
from rephorm.objects.table_section import TableSection
from rephorm.objects.table_series import TableSeries

# Adjustment for text width, because fpdf does not calculate it correctly
# Todo: Investigate why, and if it is possible to fix it
magic_number = 10

def get_max_numerical_width(table, pdf, font_family, font_size, biggest_nr, table_element=None, max_width = 0):
    """
    Determine the maximum width needed for numerical values in the table.
    Ensures width does not exceed max_width.

    How it works: Finds the longest formatted numerical string within the whole table
    """
    pdf.set_font(font_family, size=font_size)
    max_cap = pdf.get_string_width(str(biggest_nr)) + magic_number

    table_element = table_element if table_element else table

    for child in table_element.CHILDREN:
        if isinstance(child, TableSeries):
            series_data = child.data.get_values(child.settings.span)
            for value in series_data:
                formatted_value = f"{value:.{child.settings.decimal_precision}f}"
                text_width = pdf.get_string_width(str(formatted_value)) + magic_number
                if text_width > max_width:
                    max_width = min(text_width, max_cap)

        elif isinstance(child, TableSection):
            section_max_width = get_max_numerical_width(table, pdf, font_family, font_size, biggest_nr, child, max_width)
            max_width = max(max_width, section_max_width)

    return max_width

def get_max_width(table, pdf, font_family, font_size, table_element = None, parameter: Literal["title", "unit"] = "unit", max_width = 0):

    pdf.set_font(font_family, size=font_size)

    table_element = table_element if table_element else table

    for child in table_element.CHILDREN:

        if isinstance(child, TableSeries):
            attr_value = getattr(child, parameter)
            if attr_value is not None:
                text_width = pdf.get_string_width(attr_value) + magic_number
                if text_width > max_width:
                    max_width = text_width

        elif isinstance(child, TableSection):
            if parameter == "title":
                section_title_width = pdf.get_string_width(child.TITLE) + magic_number
                if section_title_width > max_width:
                    max_width = section_title_width
            section_max_width = get_max_width(table, pdf, font_family, font_size, child, parameter)
            max_width = max(max_width, section_max_width)
    return max_width