import copy
from typing import Optional, Union, List

from rephorm.object_mappers.chapter_mapper import ChapterMapper
from rephorm.objects.chart import Chart
from rephorm.objects.page_break import PageBreak
from rephorm.objects.grid import Grid
from rephorm.objects._utilities.settings_container import SettingsContainer
from rephorm.objects.table import Table
from rephorm.objects.text import Text
from rephorm.decorators.settings_validation import validate_kwargs
from rephorm.utility.add_style_prefix import add_prefix_to_styles


class Chapter:
    @validate_kwargs
    def __init__(self, title: str = None, footnotes: Optional[List[str]] = None, **kwargs):
        """
            :param title: (str) Title of the chapter.
            :key styles (Dict): Styles dictionary for additional customization (for details refer to report object).
        """
        self.title = title
        self.footnotes = footnotes
        self.CHILDREN = []
        # if "styles" in kwargs:
        #     kwargs["styles"]=adjust_styles(kwargs["styles"], caller)
        self.settings = SettingsContainer(**kwargs)
        if hasattr(self.settings, "styles"):
            self.settings.styles = add_prefix_to_styles("chapter", self.settings.styles)

    def add(
        self,
        chapter_child: Union[Grid, Table, Text, PageBreak, Chart] = None,
    ):
        if chapter_child is not None and isinstance(chapter_child, (Grid, Table, Text, PageBreak, Chart)):
            copy_chapter_child = copy.deepcopy(chapter_child)
            self.CHILDREN.append(copy_chapter_child)
        else: raise Exception("Chapter: chapter child of wrong type or None")

    def _get_mapper(self):
        return ChapterMapper(self)

    def __repr__(self):
        return f"{type(self).__name__}"