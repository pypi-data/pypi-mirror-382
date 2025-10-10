from fpdf import FPDF, enums

# Todo: The right place for this is mapper package.
def get_page_dimensions(pdf: FPDF):
    return pdf.w, pdf.h

# Todo: The right place for this is mapper package.
# Todo: 03/31/2025: Kinda useless function. This could be done in the report mapper.

def set_title_page(pdf: FPDF, report_obj):

    bool(report_obj.title) and set_title(pdf, report_obj)
    bool(report_obj.abstract) and set_abstract(pdf, report_obj)
    pdf.add_page()

def set_title(pdf: FPDF, report_obj):

    title_height = report_obj.settings.styles["report"]["title"]["font_size"]

    space_between = title_height

    title_y_pos = pdf.eph / 2 - title_height / 2

    pdf.set_y(title_y_pos)

    pdf.set_font(report_obj.settings.styles["report"]["title"]["font_family"],
                 report_obj.settings.styles["report"]["title"]["font_style"],
                 report_obj.settings.styles["report"]["title"]["font_size"])

    pdf.cell(
        text=report_obj.title,
        w=0,
        align="C",
        # Moves cursor to new ln, same behavior as in multi_cell,
        # Necessary to get same space between, when using pdf.ln
        new_y=enums.YPos.NEXT
    )

    pdf.ln(space_between)

    pdf.set_font(report_obj.settings.styles["report"]["subtitle"]["font_family"],
                 report_obj.settings.styles["report"]["subtitle"]["font_style"],
                 report_obj.settings.styles["report"]["subtitle"]["font_size"])

    pdf.multi_cell(
        text=report_obj.subtitle,
        w=0,
        align="C",
    )
    pdf.ln(space_between)

    if bool(report_obj.settings.logo):
        logo_height = report_obj.settings.styles["report"]["logo_height"] # Todo: should get extracted to logo height - styles/params.!! Extract to styles
        pdf.image(
            report_obj.settings.logo,
            x=enums.Align.C,
            y=pdf.get_y(),
            h=logo_height,
        )

    # reset the font
    pdf.set_font(
        family = report_obj.settings.styles["report"]["font_family"],
        style = report_obj.settings.styles["report"]["font_style"],
    )

def set_abstract(pdf: FPDF, report_obj):

    rs = report_obj.settings.styles["report"]
    abstract_y_pos = pdf.h - pdf.b_margin - rs["abstract"]["height"]
    abstract_font_size= rs["abstract"]["font_size"]
    abstract_text = report_obj.abstract

    line_height = 1.5
    pdf.set_font(family=rs["abstract"]["font_family"], size=abstract_font_size)

    pdf.set_y(abstract_y_pos)

    pdf.set_draw_color(0, 0, 0)
    pdf.line(x1=pdf.l_margin, y1=abstract_y_pos - 5, x2=pdf.w-pdf.r_margin, y2=abstract_y_pos - 5)

    b_margin = pdf.b_margin

    pdf.set_auto_page_break(auto=False)

    pdf.multi_cell(
        text=abstract_text,
        w=0,
        h = abstract_font_size * line_height, # Todo consider extracting this 1.5 multiplier
        align="l", # Todo: Consider extracting to styles
    )

    pdf.set_auto_page_break(auto=True, margin=b_margin)
