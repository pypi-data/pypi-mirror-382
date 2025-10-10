"""
pdf.b_margin = b.margin + footer_height + footer_top_margin.
"""
class LayoutManager:
    def __init__(self, pdf, used_top_height = 0):
        """
        Initialize the layout manager with pdf instance, and header and footer height.
        """
        self.pdf = pdf
        self.used_top_height = used_top_height

    def calculate_position(self, layout, nrow, ncol):
        """
        Here we compute grid layout based on user inputs and return array with every element X Y W H "coordinates"
        Result - array with coordinates of each element and key is (row_indx, col_indx)
        """
        result={}

        cell_width = ((self.pdf.w - self.pdf.l_margin - self.pdf.r_margin) / ncol)
        # b_margin = b_margin + footer_height + footer_top_margin
        cell_height = (self.pdf.h - self.pdf.b_margin - self.used_top_height) / nrow

        for row_indx in range (nrow):
            for col_indx in range(ncol):
                cell = layout[row_indx][col_indx]

                if cell is None:
                    continue

                rowspan = cell.get("rowspan", 1)
                colspan = cell.get("colspan", 1)

                width = colspan * cell_width
                height = rowspan * cell_height

                x = col_indx * cell_width + self.pdf.l_margin # sets from left
                y = row_indx * cell_height + self.used_top_height # sets from top

                result[(row_indx, col_indx)] = {
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height
                }

        return result

    def get_default_layout(self):
        """
        Gets the position (x, y) and available size (width, height) for a chapter or report,
        considering headers and footers to determine the exact placement of its content (child object).
        """
        available_width = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin
        available_height = self.pdf.h - self.pdf.t_margin - self.pdf.b_margin - self.used_top_height

        x = self.pdf.l_margin
        y = self.used_top_height + self.pdf.t_margin

        return x, y, available_width, available_height
