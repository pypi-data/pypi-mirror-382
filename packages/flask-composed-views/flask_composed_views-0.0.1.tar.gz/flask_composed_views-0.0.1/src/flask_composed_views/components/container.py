from .base_component import BaseComponent
from .div import Div

class Container(BaseComponent):
    def __init__(self,
                 id = None,
                 classes = None,
                 title: BaseComponent | None = None,
                 children: list[BaseComponent] | None = None):
        container_classes = "container mx-auto"
        if(classes):
            classes = " ".join([ classes, container_classes ])
        else:
            classes = container_classes
        if(children is None):
            children = []
        if(title is not None):
            children.insert(0, Div(children=[title]))
        container = Div(children=children, id=id, classes=classes)
        super().__init__(id=id, classes=classes, children=[ container ])

