from fpdf import enums

# Todo add some space after line, between line and first footnote

def add_footnotes_at_bottom(pdf, footnotes, reference_nr, last_y = None, **kwargs):

    font_size = kwargs.get('font_size')
    font_family = kwargs.get('font_family')
    font_style = kwargs.get('font_style')
    footer_padding = kwargs.get('footer_padding')
    footer_top_margin = kwargs.get('footer_top_margin')


    bottom_padding = 10
    b_margin = pdf.b_margin

    # prevent auto page break - this is a MUST!!!!!
    # else it would push content and footnotes to new page if slightly overflows
    pdf.set_auto_page_break(auto=False)

    pdf.set_font(font_family, font_style, font_size)

    #Sets line color above the footnotes
    pdf.set_draw_color(0, 0, 0)

    # current b_margin = page_margin_bottom + footer_height + footer_top_margin
    footer_position = pdf.h - b_margin + footer_top_margin

    if last_y is None:
        footnote_y_position = pdf.h - b_margin + footer_padding + footer_top_margin
        pdf.line(x1=pdf.l_margin, y1=footer_position, x2=pdf.w - pdf.r_margin, y2=footer_position)
    else:
        footnote_y_position = last_y

    pdf.set_y(footnote_y_position)

    for ref, footnote in zip(reference_nr, footnotes):
        formatted_footnote = f"[{ref}] {footnote}"
        pdf.multi_cell(w=pdf.w - pdf.l_margin - pdf.r_margin, h=None, text=formatted_footnote, align='L', new_x=enums.XPos.LEFT)
        last_y = pdf.get_y() + bottom_padding

    # Reset auto page break and b_margin
    # Todo: drop footer height, rename footer padding to bottom_margin_padding, and footnotes pos y would be pdf.h - b.margin
    pdf.set_auto_page_break(auto=True, margin = b_margin)

    return last_y
