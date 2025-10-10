from .base_tag import BaseTag

class Header1(BaseTag):
    def __init__(self,
                 children: list | None = None,
                 id: str | None = None,
                 classes: str | None = None):
        super().__init__('h1', id=id, classes=classes, children=children)
    
