from .base_tag import BaseTag

class Span(BaseTag):
    def __init__(self,
                 children: list | None = None,
                 id: str | None = None,
                 classes: str | None = None):
        super().__init__('span', id=id, classes=classes, children=children)
    