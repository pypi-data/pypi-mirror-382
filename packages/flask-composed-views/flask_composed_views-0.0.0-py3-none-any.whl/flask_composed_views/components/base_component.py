class BaseComponent:
    def __init__(self,
                 id: str | None = None,
                 classes: str | None = None,
                 children: list[object] | None = None):
        self.id = id
        self.classes = classes if(classes) else ""
        #if(isinstance(children, str)):
        #    print(f'children is a string: "{children}"')
        #print(f'children before: "{children}"')
        if(not isinstance(children, list)):
            if(children is None):
                children = []
            else:
                children = [ children ]
        #print(f'children after: "{children}"')
        self.children = children

    def _merge_render(self, *rendered_elements) -> str:
        return "".join(*rendered_elements)

    def render(self) -> str: # normally to be overriden
        rendered_children = self._merge_render(child.render() for child in self.children if(child is not None))
        return rendered_children
    
    def _copy_objects(self):
        # aber wofür? idc
        pass