from __future__ import annotations
import copy
from typing import Optional, Union, List

from rephorm.objects.table import Table
from rephorm.objects.text import Text
from rephorm.objects.chart import Chart
from rephorm.object_mappers.grid_mapper import GridMapper
from rephorm.objects._utilities.settings_container import SettingsContainer
from rephorm.decorators.settings_validation import validate_kwargs
from rephorm.utility.add_style_prefix import add_prefix_to_styles


class Grid:

    @validate_kwargs
    def __init__(self, title: str = "", footnotes: Optional[List[str]] = None, **kwargs):
        """
            :param title: (str) Title of the grid.
            :param footnotes: (Tuple(str)) Footnotes for the title.
            :key ncol (int): Number of columns in the grid.
            :key nrow (int): Number of rows in the grid.
            :key layout (Dict): layout configuration for the chart (see documentation).
            :key styles (Dict): Styles dict (refer to documentation).
        """
        self.title = title
        self.CHILDREN = []
        self.footnotes = footnotes
        self.settings = SettingsContainer(**kwargs)
        if hasattr(self.settings, "styles"):
            self.settings.styles = add_prefix_to_styles("grid", self.settings.styles)

    def add(
        self,
        grid_child : Union[Grid, Table, Text, Chart] = None,
    ):
        #12/10/2024: We should have checks in the objects and not object mappers
        # We would also not have problem with imports here, because this module itself is within OBJECTS
        # Todo: Update latest docs, explaining it is not possible to nest grids within grids, and the reason why.
        if grid_child is not None and isinstance(grid_child, (Table, Grid, Text, Chart)):
            # grid_child._on_add_callback()
            copy_grid_child = copy.deepcopy(grid_child)
            self.CHILDREN.append(copy_grid_child)
        else: raise Exception("Grid: grid child of wrong type or None")


    def _get_mapper(self):
        return GridMapper(self)

    def __repr__(self):
        return f"{type(self).__name__}"

    def _on_add_callback(self):
        pass
    # This would be called by whoever is adding the grid object.