class Footnote:
    # ----------------------------------
    # Class initiator
    # ----------------------------------

    def __init__(
        self,
        text: str = "",
    ):
        self.TEXT = text

    def __repr__(self):
        return f"{type(self).__name__}"
