from rephorm.object_mappers.page_break_mapper import PageBreakMapper


class PageBreak:

    def __init__(self, ):
        pass

    def _get_mapper(self):
        return PageBreakMapper(self)

    def __repr__(self):
        return f"{type(self).__name__}"