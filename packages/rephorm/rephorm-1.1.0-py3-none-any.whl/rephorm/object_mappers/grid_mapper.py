from rephorm.object_mappers._utilities.grid_mapper_utility import compute_grid_layout
from rephorm.utility.report.add_footnotes import add_footnotes_at_bottom
from rephorm.utility.report.footnotes_counter import generate_footnote_numbers
from rephorm.utility.report.layout_utility import LayoutManager
from rephorm.utility.report.title_utility import add_title_with_references


class GridMapper:
    def __init__(self, grid):
        self.grid = grid

    def add_to_pdf(self, **kwargs):

        pdf = kwargs["pdf"]
        layout = self.grid.settings.layout
        nrow = self.grid.settings.nrow
        ncol = self.grid.settings.ncol
        footer_last_y = kwargs["footer_last_y"] if "footer_last_y" in kwargs else None
        starting_page = pdf.page_no()
        rs = self.grid.settings.styles["report"]
        footer_top_padding = rs["footer"]["top_padding"]
        footer_top_margin = rs["footer"]["top_margin"]
        title_bottom_padding = rs["title_bottom_padding"]
        # Todo: For grid why we dont take as in chapter? The used top height calculation?
        #  What is the reason to have Y coming from kwargs? Because then it takes Y from chapter/report layout calculations,
        #  and here it passes to layout... So I guess this is what offsets it differently, when adding chart to
        #  report/chapter directly and when having it inside 1x1 grid
        y = kwargs["y"]
        grid_size = self.grid.settings.ncol * self.grid.settings.nrow

        if layout is None:
            layout = compute_grid_layout(nrow=nrow, ncol=ncol)

        if len(self.grid.CHILDREN) > grid_size:
            raise Exception(
                f"Grid capacity exceeded: attempting to add {len(self.grid.CHILDREN)} object(-s) to a grid with capacity for only "
                f"{grid_size} object(-s) ({self.grid.settings.ncol}x{self.grid.settings.nrow}). "
                f"Please either increase grid size or reduce the number of objects."
            )

        footnote_references = generate_footnote_numbers(self.grid.footnotes)
        y = add_title_with_references(pdf, self.grid.title, footnote_references,
                                  self.grid.settings.styles["grid"]["title"]["font_family"],
                                  self.grid.settings.styles["grid"]["title"]["font_size"],
                                  self.grid.settings.styles["grid"]["title"]["font_style"], title_y=y)

        if bool(self.grid.footnotes):

                footer_last_y = add_footnotes_at_bottom(
                    pdf,
                    self.grid.footnotes,
                    footnote_references,
                    last_y=footer_last_y,
                    font_family=self.grid.settings.styles["footnotes"]["font_family"],
                    font_size=self.grid.settings.styles["footnotes"]["font_size"],
                    font_style=self.grid.settings.styles["footnotes"]["font_style"],
                    footer_padding=footer_top_padding,
                    footer_top_margin=footer_top_margin,
                )

        layout_manager = LayoutManager(
            pdf=pdf,
            used_top_height=y+title_bottom_padding,
        )

        positions = layout_manager.calculate_position(layout=layout, nrow=nrow, ncol=ncol)
        valid_positions = list(positions.keys())
        # Todo: set to the last chart | Do not remove, yet
        # last_element = valid_positions[-1]
        # last_element_data = positions[last_element]
        # pdf.line(pdf.l_margin, last_element_data["y"] + last_element_data["height"], pdf.w - pdf.r_margin, last_element_data["y"] + last_element_data["height"])

        for i, item in enumerate(self.grid.CHILDREN):

            position = valid_positions[i]
            pos_data = positions[position]

            current_page = pdf.page_no()
            if current_page > starting_page:
                starting_page = current_page
                footer_last_y = None


            grid_size = self.grid.settings.ncol * self.grid.settings.nrow

            mapper = item._get_mapper()
            mapper.add_to_pdf(
                pdf=pdf,
                x=pos_data["x"],
                y=pos_data["y"],
                w=pos_data["width"],
                h=pos_data["height"],
                grid_size=grid_size,
                footer_last_y=footer_last_y,
                context="grid",
            )

            # For debugging
            # pdf.set_draw_color(255, 0, 0)
            # pdf.rect(
            #     x=pos_data["x"],
            #     y=pos_data["y"],
            #     w=pos_data["width"],
            #     h=pos_data["height"],
            # )

