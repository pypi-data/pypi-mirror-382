from .tag_builder import build_tag
from .base_component import BaseComponent

class BaseTag(BaseComponent):
    def __init__(self,
                 tag: str,
                 children: list | None = None,
                 id: str | None = None,
                 classes: str | None = None,
                 other_attributes: dict | None = None):
        self.tag = tag
        self.other_attributes = other_attributes
        super().__init__(id=id, classes=classes, children=children)
        #print(f'tag="{tag}" - children: {[c for c in children]}')
    
    def render(self):
        return build_tag(self.tag,
                         id=self.id,
                         classes=self.classes,
                         other_attributes=self.other_attributes,
                         content=super().render())
