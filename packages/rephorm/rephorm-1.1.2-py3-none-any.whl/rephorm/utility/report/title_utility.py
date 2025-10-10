import fpdf

def add_title_with_references(pdf, title, references, font_family, font_size, font_style, title_y, cell_width=None):

    # default fall back
    cell_width = cell_width or pdf.epw

    # anchor_x - starting x coordinate
    anchor_x = pdf.l_margin if cell_width == pdf.epw else pdf.get_x()

    pdf.set_font(font_family, font_style, font_size)

    actual_title_width = pdf.get_string_width(title)

    center_x = anchor_x + (cell_width - actual_title_width) / 2

    pdf.set_xy(center_x, title_y)

    # should set this on report level (report mapper)
    pdf.c_margin = 0

    is_multiline = "\n" in title

    # avoid auto-wrapping. Only break line if user specifies.
    if is_multiline:
        pdf.multi_cell(actual_title_width, None, title, align="C")
    else:
        pdf.cell(actual_title_width, None, title, align="C", new_y=fpdf.YPos.NEXT)

    y_after_title=pdf.y

    # Todo: References will not work if it is multiline and has newlines, because it sets ref_y to title_y, when for multiline it should set to last line start Y
    #  ref_x will not work as well ...

    if references:
        pdf.set_font_size(font_size*0.5)
        spacing = 3  # Space between references

        ref_x = center_x + actual_title_width + spacing

        # Set references
        for ref in references:
            ref_text = str(f"[{ref}]")
            pdf.set_xy(ref_x, title_y)
            pdf.cell(pdf.get_string_width(ref_text), None, ref_text, 0, 0, "L")
            ref_x += pdf.get_string_width(ref_text) + spacing

    # return last y pos
    return y_after_title # Todo: Check why not pdf.get_y() and pdf.y? Also check why I cant set last Y here and then use it later. why it breaks. Why we need to return this Y at all