# OpenAPI documentation

## Generate specification file

To generate an [OpenAPI specification](https://www.openapis.org) file, use the command:

    ./manage.py makeapidoc

This will generate the file `doc/api/openapi.json`. If you prefer ton
generate the specification in Yaml format use:

    ./manage.py makeapidoc -f yaml

You ca use an [OpenAPI tool](https://tools.openapis.org/) to expose you API.

## Custom template

You can use the `PFX_OPENAPI_TEMPLATE` settings in your app to override
the default OpenAPI template.

In the following example we load the version from the app and
the description from a custom markdown file. We create 2 tags
to group Rest views.

```python
from example_app import __version__

with open(f'{BASE_DIR}/openapi/header.md') as f:
    openapi_header = f.read()
PFX_OPENAPI_TEMPLATE = {
    'title': "Example API",
    'version': __version__,
    'info': dict(description=openapi_header),
    'servers': [
        dict(
            url='https://example.org/api',
            description="Production server"),
        dict(
            url='https://stage.example.org/api',
            description="Stage server")],
    'components': dict(
        securitySchemes=dict(BearerAuth=dict(
            type='http', scheme='bearer', bearerFormat='JWT'))),
    'tags': [
        dict(name="AuthorRestView",
             description="A description about authors…"),
        dict(name="BookRestView",
             description="A description about books…")],
        dict(name="CustomTag",
             description="A description about custom tag…")],
}
```

### Tags

You ca use the tags class attribute on your view to customize the view tags:

```python
class CustomRestView(BaseRestView):
    tags = [Tag("CustomTag")]
```

By default each rest view has a tag build with the class name (here `CustomRestView`).


## Document you API

`makeapidoc` use the `@rest_api` decorator and the [APISpec](https://APISpec.readthedocs.io)
Yaml syntax in Docstrings to generate the specification of services:

```python
    @rest_api(
        "/custom", method="get")
    def get_meta(self, *args, **kwargs):
        """Entrypoint for :code:`GET /custom` route.

        :returns: The JSON response
        :rtype: :class:`JsonResponse`
        ---
        get:
            summary: Get the custom data
        """
        return JsonResponse(self.get_custom_data())
```

Everything before `---` is ignored by `makeapidoc`, then you can use any
Docstrings format of you choice. If you use a generator for the
code documentation based on Docstrings, it may be necessary to tell it
to ignore the contents of Docstrings after `---`. Refer to the
tool's documentation to do that.

Refer to the [APISpec documentation](https://APISpec.readthedocs.io)
to find out about all the possibilities.

### Path parameters

`makeapidoc` will generate the specification for all
the path parameters automatically.

You can describe the path parameters in APISpec's `parameters` section,
which will replace the generated parameter. If you just want to give
the description and keep the values generated for the parameter,
you can use the `extra parameters` section (specific to `makeapidoc`):

You can use `{model}` in the spec to insert the `View.model` verbose name,
and `{models}` for the plural form (useful for generic mixins).

```python
@rest_api("/<int:id>", method="get")
def get(self, id, *args, **kwargs):
    """Entrypoint for :code:`GET /<int:id>` route.

    Retrieve an object detail by ID.

    :returns: The JSON response
    :rtype: :class:`JsonResponse`
    ---
    get:
        summary: Get {model}
        parameters extras:
            id: the {model} pk
    """
```

### Query parameters

Query parameters are get in the code and cannot be generated.

You can describe the query parameter in APISpec's `parameters` section,
but if you want to describe parameters that can be used in many services,
you can write a custom class for you parameter and pass a parameters
list to the `@rest_api` decorator:

```
from pfx.pfxcore.apidoc import QueryParameter, register_global_parameter

class ListCount(QueryParameter):
    """Total objects count in response (`meta.count`).

    * if `false` (default value), `meta.count` is not returned
    * if `true`, `meta.count` is returned

    If this attribute is set, `items` will be returned only if
    `items` attribute is explicitly `true`.
    """
    name = 'count'
    schema = dict(type='boolean', default=False)

register_global_parameter(ListCount)

class ListGroup(ParameterGroup):
    parameters = [ListCount]
```

```python
from .parameters import ListGroup

@rest_api("/", method="get", parameters=[ListGroup])
```

#### Pre defined query parameters

A number of predefined parameters and groups are used by view mixins, and are reusable and inheritable:
See [API reference | Query parameters & groups](api.views.rst#query-parameters-groups) for details.

For {class}`pfx.pfxcore.views.parameters.ListSearch`, you can redefine the behaviour by annotation:
either with `@rest_doc` on the view (useful if the view inherits from {class}`pfx.pfxcore.views.ListRestViewMixin`),
or with `@rest_api` on the service (useful if you reuse the {class}`pfx.pfxcore.views.parameters.ListSearch` parameter
or the {class}`pfx.pfxcore.views.parameters.groups.List` group).

```python
from pfx.pfxcore.decorator.rest import rest_doc, rest_view
from pfx.pfxcore.views import BaseRestView, ListRestViewMixin

# Do not add the search param in api doc:
@rest_doc("", "get", search=False)
@rest_view("/my-view")
class MyView(ListRestViewMixin, BaseRestView):
    pass
```

```python
from pfx.pfxcore.decorator.rest import rest_doc, rest_view
from pfx.pfxcore.views import BaseRestView, ListRestViewMixin

# Customize the search param description in api doc:
@rest_doc("", "get", search="Search the string in name and summary fields.")
@rest_view("/my-view")
class MyView(ListRestViewMixin, BaseRestView):
    pass
```

```python
from pfx.pfxcore.decorator.rest import rest_doc, rest_view
from pfx.pfxcore.views import BaseRestView

@rest_view("/custom")
class MyView(BaseRestView):

    # Use parameters.groups.List with custom description for search param:
    @rest_api(
        "", method="get",
        parameters=[parameters.groups.List],
        search="A custom description.")
    def get(self, *args, **kwargs):
        return JsonResponse({})
```


### Body and response schema

When using standard mixins to provide basic Rest services, the body
and response schemas are automatically generated using
the view's `fields` and `list_fields` attributes.

For the response you can add the specification for object fields
in `json_repr()` Docstrings:

```python
def json_repr(self, **values):
    """JSON representation.
    ---
    user:
        type: object
        properties:
            my_number:
                type: number
            my_name:
                type: string
    """
    values.update(
        my_number=123,
        my_name="Example")
    return super().json_repr(**values)
```

`makeapidoc` will merge all `json_repr()` Docstrings recursively
following the python class inheritance.

#### Custom schemas

You can add custom schemas for your custom services. You have to follow these 3 steps:

1. Generate the schemas in the `generate_schemas` class method.
2. Add the schemas in the `get_apidoc_schemas` class method result.

Don't forget to call the super method in these methods to keep
defaults generated schemas.

You can use `pfx.pfxcore.apidoc.ModelSchema` to build a schema from a model
or `pfx.pfxcore.apidoc.Schema` to build a schema from scratch.

You can use `request_schema` and `response_schema` `@rest_api` attributes
to set the schemas as a request body schema and as a response schema for a service.

Example:

```python
from pfx.pfxcore.apidoc import ModelSchema, Schema

class CustomRestView(RestView):
    @rest_api(
        "/custom", method="post",
        request_schema='custom_schema', response_schema='my_model_schema')
    def custom_post(self, *args, **kwargs):
        # …

    @classmethod
    def generate_schemas(cls):
        """Generate schemas for the class.
        """
        from .fields import FieldType
        super().generate_schemas()
        cls.custom_schema = Schema('custom_schema', "Custom", properties=dict(
            fields=dict(
                type='array', items=dict(type='object', properties=dict(
                    a_string=dict(type='string'),
                    an_enum=dict(
                        type='string',
                        enum=list('value1', 'value2')),
                    a_string_list=dict(
                        type='array', items=dict(type='string'),
                        example=["value1", "value2"]),
                    a_bool=dict(type='boolean'))),
                description="Custom object.")))
        cls.my_model_schema = ModelSchema(MyModel, cls._process_fields([
                'field1', 'field2', 'field3']))

    @classmethod
    def get_apidoc_schemas(cls):
        """Get schemas for the class.

        :returns: The schemas list
        :rtype: :class:`list[pfx.pfxcore.apidoc.Schema]`
        """
        return super().get_apidoc_schemas() + [cls.custom_schema, cls.my_model_schema]
```
