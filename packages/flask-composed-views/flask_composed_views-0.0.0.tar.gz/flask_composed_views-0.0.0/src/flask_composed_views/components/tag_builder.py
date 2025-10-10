import html

def merge_classes(classes: str | list[str|None] | None, merger_tool=None) -> str:
    """
    how i meant to use it:
    ```python
    from tailwind_merge import TailwindMerge 
    class_merger = TailwindMerge()
    merge_classes(classes, merger_tool=lambda cl: class_merger.merge(*cl))
    ```
    or something like that
    """
    if(classes is None):
        return None
    if(not isinstance(classes, str)):
        classes = [ cl for cl in classes if(cl) ]
    if(merger_tool is not None): # use tailwind-merge for example
        merged_classes = merger_tool(classes)
    else:
        if(not isinstance(classes, str)):
            merged_classes = " ".join(c for c in classes if(c))
        else:
            merged_classes = classes
    return merged_classes

def build_tag(tag: str,
              id: str | None = None,
              classes: str | None = None,
              merger_tool = None,
              content: str | None = None,
              id_is_safe: bool = False,
              safe: bool=True,
              other_attributes: dict | None = None,
              ) -> str:
    """
    content is expected to be the output of render() methods hence considered a priori "safe"
    classes are considered safe a priori
    id: idk, maybe i'd have the bad idea of using user inputs as part of an id because im stupid
    """
    classes = merge_classes(classes, merger_tool=merger_tool)
    if(id and not id_is_safe):
        id = html.escape(id)
    rendered = f'<{tag}'
    if(id):
        rendered += f' id="{id}"'
    if(classes):
        rendered += f' class="{classes}"'
    if(other_attributes):
        for attr_name, attr_val in other_attributes.items():
            rendered += f' {attr_name}="{attr_val}"'
    rendered += '>'
    if(content):
        if(not safe):
            content = html.escape(content)
        rendered += f'{content}</{tag}>'
    return rendered



