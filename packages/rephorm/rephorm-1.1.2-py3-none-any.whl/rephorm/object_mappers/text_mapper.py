from rephorm.utility.report.title_utility import add_title_with_references


class TextMapper:
    def __init__(self, text):
        self.text = text

    def add_to_pdf(self, **kwargs):
        pdf = kwargs["pdf"]
        w = kwargs["w"]
        y = kwargs["y"]
        x = kwargs["x"]

        family = self.text.settings.styles["text"]["title"]["font_family"]
        size = self.text.settings.styles["text"]["title"]["font_size"]
        style = self.text.settings.styles["text"]["title"]["font_style"]

        # todo: check multipliers everywhere and use line height const for it.
        line_height = 1.5 # todo: consider extracting to styles, once again.

        y = add_title_with_references(pdf=pdf, title=self.text.title, references=None,
                                  font_family=family, font_size=size, font_style=style, title_y=y)

        pdf.set_font(family=self.text.settings.styles["text"]["font_family"],
                     size=self.text.settings.styles["text"]["font_size"],
                     style=self.text.settings.styles["text"]["font_style"])

        pdf.set_xy(x, y)

        pdf.multi_cell(
            w=w,
            h=self.text.settings.styles["text"]["font_size"] * line_height,
            txt=self.text.TEXT,
            align=self.text.align,
            markdown=self.text.markdown,
        )
