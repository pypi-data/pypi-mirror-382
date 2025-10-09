# Django PFX Views
REST services are provided as `ViewMixin` for `BaseRestView`.
Each of these views must set the queryset used to query the model data either
by defining the queryset attribute or by overriding the `get_queryset` method.

Fields can be listed in the fields attribute, else all the fields are provided.

## DetailRestViewMixin
Provide a get detail service for a model class.

By default, all model fields are included in response. You can customize
the response by specifying the fields attribute (see [Define Fields](pfx_views.md#define-fields) for details).

```python
from pfx.pfxcore.decorator import rest_view
from pfx.pfxcore.views import BaseRestView, DetailRestViewMixin

@rest_view("/books")
class BookRestView(DetailRestViewMixin, BaseRestView):
    queryset = Book.objects
    fields = ['name', 'author', 'pub_date', 'created_at', 'type']
```

## SlugDetailRestViewMixin
Provide a get detail service for a model class with a slug.
Slug field is searched in the `slug` field of the model by default,
but it can be overridden with the `SLUG_FIELD` attribute.

```python
from pfx.pfxcore.decorator import rest_view
from pfx.pfxcore.views import BaseRestView, SlugDetailRestViewMixin

@rest_view("/authors")
class AuthorRestView(SlugDetailRestViewMixin, BaseRestView):
    queryset = Author.objects
    SLUG_FIELD = "slug"
    fields = ['name', 'slug', 'created_at', 'type']
```

## ListRestViewMixin
Provide a list service for a model class.

By default, list fields are taken from fields attributes.
They can also be listed in the list_fields attribute if you need to have
different fields in the list than in other views.
```python
from pfx.pfxcore.decorator import rest_view
from pfx.pfxcore.views import BaseRestView, ListRestViewMixin

@rest_view("/books")
class BookRestView(ListRestViewMixin, BaseRestView):
    queryset = Book.objects
    list_fields = ['name', 'author', 'pub_date', 'created_at', 'type']
```

### Pagination
If you pass `?subset=pagination`, the response will include pagination data in meta:
```python
{
    "items": ['…'],
    "meta": {
        "page": 1,
        "page_size": 10,
        "count": 200,
        "page_count": 20,
        "subset": [1, 2, 3, 4, 5],
        "page_subset": 5
    }
}
```
The page_size cannot be greater than `PFX_MAX_LIST_RESULT_SIZE` settings.
Override `pagination_result(self, qs)` to customize the behavior.

If you pass `?subset=offset`, the response will include offset/limit data in meta:
```python
{
    "items": ['…'],
    "meta": {
        "count": 200,
        "page_count": 20,
        "limit": 10,
        "offset": 0
    }
}
```
The limit cannot be greater than `PFX_MAX_LIST_RESULT_SIZE` settings.
Override `offset_result(self, qs)` to customize the behavior.

### Filters
List view can have filters.

#### ModelFilter
Use `ModelFilter` to add a filter on an ORM field:
```python
from pfx.pfxcore.views import (
    RestView,
    ModelFilter)

class AuthorRestView(RestView):
    filters = [
        ModelFilter(Author, 'name'),
    ]
```

#### Filter
Use `Filter` to add a custom filter:
```python
from django.db.models import Q

from pfx.pfxcore.views import (
    RestView,
    FieldType,
    Filter)


def name_filter(value):
    return Q(first_name__icontains=value) | Q(last_name__icontains=value)


class AuthorRestView(RestView):
    filters = [
        Filter('name', "Name", FieldType.CharField, name_filter),
    ]
```

## CreateRestViewMixin
Provide a creation service for a model class.
```python
from pfx.pfxcore.decorator import rest_view
from pfx.pfxcore.views import BaseRestView, CreateRestViewMixin

@rest_view("/books")
class BookRestView(CreateRestViewMixin, BaseRestView):
    queryset = Book.objects
    fields = ['name', 'author', 'pub_date', 'created_at', 'type']
```

### Default values
You can set default values for fields in the ORM object field. But if
you need to set it at view level, you can use the `default_values`
class attribute.
```python
from pfx.pfxcore.decorator import rest_view
from pfx.pfxcore.views import BaseRestView, CreateRestViewMixin

@rest_view("/books")
class BookRestView(CreateRestViewMixin, BaseRestView):
    queryset = Book.objects
    default_values = dict(
        format='octavo'
    )
```
If you need to set dynamics default values,
you can override following methods (depending on your needs):
* `get_default_values(self)`: return `default_values`.
* `new_object(self)`: return a new object instance with `get_default_values()`.
* `is_valid(self, obj, created=False, rel_data=None)`: persist the instance after validation.

## UpdateRestViewMixin
Provide an update service for a model class.
```python
from pfx.pfxcore.decorator import rest_view
from pfx.pfxcore.views import BaseRestView, UpdateRestViewMixin

@rest_view("/books")
class BookRestView(UpdateRestViewMixin, BaseRestView):
    queryset = Book.objects
    fields = ['name', 'author', 'pub_date', 'created_at', 'type']
```

## DeleteRestViewMixin
Provide a delete service for a model class.
```python
from pfx.pfxcore.decorator import rest_view
from pfx.pfxcore.views import BaseRestView, DeleteRestViewMixin

@rest_view("/books")
class BookRestView(DeleteRestViewMixin, BaseRestView):
    queryset = Book.objects
```

## SecuredRestViewMixin
`SecuredRestViewMixin` allows you to define whether methods
are public or private (requires a logged-in user),
and to check access conditions to the method for a user.

If you inherit `BaseRestView` or `RestView`, `SecuredRestViewMixin` is
already included. The only way to ignore it or defining your custom security
system from scratch id to inherit Django original `View` instead.

### Default behavior
By default, all methods are private. You can modify
the `default_public` attribute to change this.
```python
from pfx.pfxcore.decorator import rest_view
from pfx.pfxcore.views import RestView

@rest_view("/books")
class BookRestView(RestView):
    queryset = Book.objects
    default_public = True
```

### Public method
If you want to define specific methods as a public methods,
add corresponding attributes `${method_name}_public`:
```python
from pfx.pfxcore.decorator import rest_view
from pfx.pfxcore.views import RestView

@rest_view("/books")
class BookRestView(RestView):
    queryset = Book.objects
    get_public = True
    get_list_public = True
```

### Check user access
For private methods, you can verify user access in two steps:
* By overriding the `perm(self)` method.
* By overriding the `${method_name}_perm(self)` method.

the `perm` method is called first, and if it returns `false`, access is denied.
If it returns `true` (default behavior), access is allowed
if `${method_name}_perm(self)` method does not exists.
If `${method_name}_perm` exists, it is called and must
return `true` to allow access.
```python
from pfx.pfxcore.decorator import rest_view
from pfx.pfxcore.views import RestView

@rest_view("/books")
class BookRestView(RestView):
    queryset = Book.objects

    def my_method_perm(self):
        return self.request.user.is_admin
```

### Check user access based on data
You can check user access based on data by overriding following methods:
* `object_create_perm(self, data)`
* `object_update_perm(self, obj, data)`
* `object_delete_perm(self, obj)`
Where `data` is the dictionary of new values and `obj` the existing object.

These methods are called by the put/post/delete methods of standard mixins
before validation. If you write a custom method and you want to use
one of these method, you have to call it yourself.

## Base classes
You can use PFX view mixins with following base classes:

* `View`: the Django base view class.
* `BaseRestView`: The PFX base view for API, inherits `SecuredRestViewMixin` and `View`.
* `RestView`: The PFX base view for a Rest API, inherits:
  * `ListRestViewMixin`
  * `DetailRestViewMixin`
  * `CreateRestViewMixin`
  * `UpdateRestViewMixin`
  * `DeleteRestViewMixin`
  * `BaseRestView`

## Define Fields
Fields in `fields` and `list_fields` attributes can be:
* A string: the field attribute name.
* A `pfx.pfxcore.views.VF` object.

`VF` object can be used to customize field behavior and must define at least the field name:
```
field = [VF('name')]
```
You can specify following optional attributes:
* `verbose_name`
* `field_type`
* `alias`
* `readonly`
* `readonly_create`
* `readonly_update`
* `choices`
* `select`
* `json_repr`

Refer to method documentation for details.

### Meta

The `ModelResponseMixin` (included in every mixin with a service whose response is a simple object),
exposes a `/meta` service to identify fields (and their characteristics: type, required, readonly, ...),
to enable automatic generation of forms.

See the generated API documentation for more details.

On the same principle, `ListRestViewMixin` exposes the `/meta/list` service, which,
in addition to the fields, returns the list of available filters and
the list of available fields to order the list.

#### Notes for future releases

In a future version, these services should return a JSON OpenAPI structure. The list
of orderable fields is resource-intensive to compute and should be removed and moved
in the generated API doc.

## Custom service with body validation

You can define a custom service and load body data into a unmanaged model if you view
inherits from `BodyMixin`.

Then you can add custom validators on you model.

Define an unmanaged model (you can use fields validators or extend the `clean` method
to customize validation):
```python
from django.db import models
from django.utils.translation import gettext_lazy as _

from pfx.pfxcore.models import PFXModelMixin


class CustomModel(PFXModelMixin, models.Model):
    pks = models.IntegerField(_("An integer"))

    class Meta:
        managed = False
```

Then you can load the body in a `CustomModel` instance in a service, method `body_to_model`
will call `full_clean` on model instance and raise a `ModelValidationAPIError` if
there is invalid values (`ModelValidationAPIError` will be automatically converted
into a `422/JSONResponse` including fields and/or global errors):
```python
from pfx.pfxcore.decorator import rest_api, rest_view
from pfx.pfxcore.views import BodyMixin

from .models import CustomModel


@rest_view("/my-service")
class MyServiceView(BodyMixin):
    @rest_api("", method="put")
    def put(self, *args, **kwargs):
        custom = self.body_to_model(CustomModel)
        # …
```

See {func}`pfx.pfxcore.views.BodyMixin.body_to_model` for method documentation.
