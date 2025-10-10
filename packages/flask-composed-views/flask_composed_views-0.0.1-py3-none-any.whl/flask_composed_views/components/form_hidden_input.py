from .base_tag import BaseTag

class FormHiddenInput(BaseTag):
    def __init__(self, id = None, classes = None, other_attributes = None):
        if(other_attributes is None):
            other_attributes = {}
        other_attributes['type'] = 'hidden'
        super().__init__(tag='input',
                         id=id,
                         classes=classes,
                         other_attributes=other_attributes,
                         children=None)

