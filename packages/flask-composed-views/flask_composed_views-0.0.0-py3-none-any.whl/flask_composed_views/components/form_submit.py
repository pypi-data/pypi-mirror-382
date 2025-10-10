from .base_tag import BaseTag
from .base_component import BaseComponent

class FormSubmit(BaseTag):
    def __init__(self, label: BaseComponent, id = None, classes = None,):
        super().__init__(tag='button',
                         id=id,
                         classes=classes,
                         other_attributes = {
                             'type': 'submit',
                         },
                         children = [ label, ])

