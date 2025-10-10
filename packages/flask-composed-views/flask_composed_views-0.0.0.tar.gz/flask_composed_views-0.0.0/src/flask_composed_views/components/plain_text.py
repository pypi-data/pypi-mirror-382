import html

from .base_component import BaseComponent

class PlainText(BaseComponent):
    def __init__(self,
                 text: str,
                 safe: bool = False,):
        self.is_safe = safe
        self.text = text
        super().__init__()

    def render(self):
        rendered = self.text
        if(not self.is_safe):
            rendered = html.escape(rendered)
        return rendered

def this_is_text(text: str, safe: bool = False) -> str:
    return PlainText(text, safe).render()

