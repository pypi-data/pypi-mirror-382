from .base_component import BaseComponent
from .base_tag import BaseTag

class FormTextInput(BaseComponent):
    def __init__(self,
                 label: BaseComponent | None = None,
                 name: str | None = None,
                 id: str | None = None,
                 classes: str | None = None,
                 max_len: int | None = None,):
        children = []
        if(label):
            label_element = BaseTag(tag='label',
                                    other_attributes={
                                        'for': name,
                                    },
                                    children=[ label, ])
            children.append(label_element)
        input_attributes = {
            'type': 'text',
        }
        if(name):
            input_attributes['name'] = name
        if(max_len):
            input_attributes['max_len'] = str(max_len)
        input_element = BaseTag(tag='input',
                                id=id,
                                classes=classes,
                                other_attributes=input_attributes,
                                children=None)
        children.append(input_element)
        super().__init__(id, classes, children)

