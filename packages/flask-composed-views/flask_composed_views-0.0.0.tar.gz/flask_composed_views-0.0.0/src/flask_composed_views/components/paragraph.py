from .base_tag import BaseTag

class Paragraph(BaseTag):
    def __init__(self,
                 children: list | None = None,
                 id: str | None = None,
                 classes: str | None = None):
        super().__init__('p', id=id, classes=classes, children=children)
    
