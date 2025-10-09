# View decorator and URL
## @rest_view
Used to provide the base path of a view class
```python
from pfx.pfxcore.decorator import rest_view

@rest_view("/base-path")
class ViewClass():
```

## @rest_api
Used to annotate the rest services method.
Parameters are the path and the HTTP method.
```python
from pfx.pfxcore.decorator import rest_api

@rest_api("/path", method="get")
def class_method(self):
```

A short example
```python
from pfx.pfxcore.decorator import rest_view, rest_api
from pfx.pfxcore.http import JsonResponse

@rest_view("/books")
class BookRestView():

    @rest_api("/list", method="get")
    def get_list(self):
        return JsonResponse(
            dict(books=['The Man in the High Castle', 'A Scanner Darkly']))
```

### path parameters
Path can contain parameters that are passed to the method.
```python
from pfx.pfxcore.decorator import rest_api

@rest_api("/path/<int:pk>/test/<slug:slug>", method="get")
def class_method(self, pk, slug):
```

## Registering urls
To be available, annotated view class must be registered
in your urls.py file as follows.

```python
from pfx.pfxcore import register_views

from . import views

urlpatterns = register_views(
    views.AuthorRestView,
    views.BookRestView)
```

You can include multiple views under one path, or add a path
wih a specific class method for each HTTP methods:
```python
from django.urls import include, path
from pfx.pfxcore import register_views

from . import views

urlpatterns = [
    path('api/', include(register_views(
        views.AuthorRestView,
        views.BookRestView))),
    path('other/thing', views.OtherRestView.as_view(
        pfx_methods=dict(get='get_other'))),
]
```
