from typing import Literal
from rephorm.decorators.settings_validation import validate_kwargs
from rephorm.object_mappers.text_mapper import TextMapper
from rephorm.objects._utilities.settings_container import SettingsContainer


class Text:
    # ----------------------------------
    # Class initiator
    # ----------------------------------
    @validate_kwargs
    def __init__(
        self,
        title: str = "",
        text: str = "",
        align: Literal["x", "c", "l", "j", "r"] = "j",
        markdown = False,
        **kwargs
    ):
        self.title = title
        self.TEXT = text
        self.align = align
        self.markdown = markdown
        self.settings = SettingsContainer(**kwargs)

    def _get_mapper(self):
        return TextMapper(self)

    def __repr__(self):
        return f"{type(self).__name__}"





