This module defines classes that can be rendered as "views" in a flask application.

The following example define a form to input some text as a component class (this additionally uses tailwindcss classes):
```python
from flask_composed_views.components import BaseComponent, FormTextInput, Span, PlainText, FormSubmit

class WordInputForm(BaseComponent):
    def __init__(self, id = None, classes = None, csrf_token: str | None = None):
        form = Form(id='word-input-form',
                    classes=classes,
                    csrf_token=csrf_token,
                    action='/',
                    children=[
                        FormTextInput(label=Span(classes="p-2 font-bold",
                                                 children=PlainText('Word:', safe=True,)),
                                      name='word',
                                      id=id,
                                      classes="border-1 border-solid broder-gray-400",
                                      max_len=44),
                        FormSubmit(label=PlainText('Find'),
                                   classes=" ".join([
                                        "rounded-lg px-2 py-1 font-bold bg-yellow-200 hover:bg-yellow-300",
                                        "active:bg-yellow-200 active:border-2 active:border-yellow-200",
                                        "mx-4"
                                   ]))
                    ])
        super().__init__(id, classes, children=[form])
```
This form is rendered using:
```python
csrf_token = ... # for example, using `flask_wtf.csrf.generate_csrf`
WordInputForm(csrf_token=csrf_token).render()
```
which could theoretically be used as the output of an `@app.route`-decorated function. Normally you would embed it within a page layout, etc.
