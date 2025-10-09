from rephorm.utility.report.add_footnotes import add_footnotes_at_bottom
from rephorm.utility.report.footnotes_counter import generate_footnote_numbers
from rephorm.utility.report.layout_utility import LayoutManager
from rephorm.utility.report.title_utility import add_title_with_references


class ChapterMapper:
    def __init__(self, chapter):
        self.chapter = chapter

    # Todo: Reconsider add_to_pdf method naming. it would make more sense "render" or "map" because we do
    #  add things to the pdf and then go through the children here and eventually render them too...
    def add_to_pdf(self, **kwargs):

        pdf = kwargs["pdf"]
        footer_last_y = kwargs["footer_last_y"] if "footer_last_y" in kwargs else None
        starting_page = pdf.page_no()
        n_children = len(self.chapter.CHILDREN)


        rs = self.chapter.settings.styles["report"]
        used_top_height = rs["header"]["height"] + rs["header"]["bottom_margin"]
        footer_top_padding = rs["footer"]["top_padding"]
        footer_top_margin = rs["footer"]["top_margin"]

        pdf.set_y(used_top_height)

        pdf.set_font(
            family=self.chapter.settings.styles["chapter"]["font_family"],
            size=self.chapter.settings.styles["chapter"]["font_size"],
            style=self.chapter.settings.styles["chapter"]["font_style"],
        )

        if self.chapter.title is not None:
            footnote_references = generate_footnote_numbers(self.chapter.footnotes)
            title_y_pos = pdf.h / 2 - pdf.font_size / 2 # Todo: consider multiline title in the future (would need to calculate h of the text cell)
            add_title_with_references(pdf, self.chapter.title, footnote_references,
                                      font_family=self.chapter.settings.styles["chapter"]["title"]["font_family"],
                                      font_size=self.chapter.settings.styles["chapter"]["title"]["font_size"],
                                      font_style=self.chapter.settings.styles["chapter"]["title"]["font_style"],
                                      title_y=title_y_pos, cell_width=pdf.epw)
            if n_children > 0:
                pdf.add_page()

            if bool(self.chapter.footnotes):
                footer_last_y = add_footnotes_at_bottom(
                    pdf,
                    self.chapter.footnotes,
                    footnote_references,
                    last_y=footer_last_y,
                    font_family=self.chapter.settings.styles["footnotes"]["font_family"],
                    font_size=self.chapter.settings.styles["footnotes"]["font_size"],
                    font_style=self.chapter.settings.styles["footnotes"]["font_style"],
                    footer_padding=footer_top_padding,
                    footer_top_margin=footer_top_margin,
                )

        layout_manager = LayoutManager(
            pdf,
            used_top_height=used_top_height,
        )

        for i, item in enumerate(self.chapter.CHILDREN):

            x, y, width, height = layout_manager.get_default_layout()

            current_page_nr = pdf.page_no()
            if current_page_nr > starting_page:
                starting_page = current_page_nr
                # footer_last_y = None

            mapper = item._get_mapper()

            # TODO: IMPORTANT: Review the design and implement everything in a way where we pass single Y position
            #  across the object mappers, so we do not need Y - to set the position of chapter elements/objects,
            #  then title_y to correctly set the titles. We should pass Y along, and render elements/titles from the
            #  LAST known Y position (which is the last element rendered). This way we can avoid the need for
            #  title_y and footer_last_y, and god knows how many more Y's :D
            mapper.add_to_pdf(pdf=pdf, x=x, y=y, w=width, h=height, footer_last_y=footer_last_y)

            if i < n_children - 1:
                pdf.add_page()