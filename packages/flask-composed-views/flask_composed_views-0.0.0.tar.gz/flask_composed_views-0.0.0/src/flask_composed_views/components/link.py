from .base_tag import BaseTag


class Link(BaseTag):
    def __init__(self,
                 children = None,
                 id = None,
                 classes = None,
                 href: str | None = None):
        other_attributes = {}
        if(href):
            other_attributes['href'] = href
        super().__init__('a',
                         id=id,
                         classes=classes,
                         other_attributes=other_attributes,
                         children=children,)

