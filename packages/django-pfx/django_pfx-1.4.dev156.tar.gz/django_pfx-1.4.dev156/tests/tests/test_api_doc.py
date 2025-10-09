from io import StringIO

from django.core.management import call_command
from django.test import TestCase, override_settings

from apispec.yaml_utils import load_operations_from_docstring as from_doc

from pfx.pfxcore.management.commands.makeapidoc import (
    get_spec,
    path_parameters,
)
from pfx.pfxcore.test import TestAssertMixin
from tests.views import AuthorRestView


class ApiDocTest(TestAssertMixin, TestCase):
    def test_default_generation(self):
        spec = get_spec(set()).to_dict()
        self.assertEqual(spec['openapi'], "3.0.2")
        info = spec['info']
        self.assertEqual(info['title'], "PFX API")
        self.assertEqual(info['version'], "1.0.0")

    @override_settings(PFX_OPENAPI_TEMPLATE=dict(
        title="MyAPI",
        info=dict(description="A test API")))
    def test_default_customized_generation(self):
        spec = get_spec(set()).to_dict()
        self.assertEqual(spec['openapi'], "3.0.2")
        info = spec['info']
        self.assertEqual(info['title'], "MyAPI")
        self.assertEqual(info['version'], "1.0.0")
        self.assertEqual(info['description'], "A test API")

    @override_settings(PFX_OPENAPI_TEMPLATE=dict(
        title="MyAPI",
        info=dict(
            description="A test API"),
        components=dict(securitySchemes=dict(
            BearerAuth=dict(type='http', scheme='Bearer')))))
    def test_paths_generation(self):
        def assertMethods(paths, p, methods):
            self.assertEqual(set(paths[p].keys()), methods)

        spec = get_spec(set()).to_dict()
        paths = spec['paths']
        assertMethods(paths, '/authors', {'get', 'post'})
        assertMethods(paths, '/authors/{pk}', {'get', 'put', 'delete'})
        assertMethods(paths, '/authors/slug/{slug}', {'get'})
        assertMethods(paths, '/authors/cache/{pk}', {'get'})

        tags = spec['tags']
        tags_keys = [t['name'] for t in tags]
        self.assertIn("Authentication", tags_keys)
        self.assertIn("Author", tags_keys)
        self.assertIn("Book", tags_keys)
        self.assertIn("Book Type", tags_keys)
        self.assertIn("Locale", tags_keys)
        self.assertJE(paths['/authors'], 'get.tags', ["Author"])
        self.assertJE(paths['/authors'], 'post.tags', ["Author"])
        self.assertJE(paths['/auth/login'], 'post.tags', ["Authentication"])

        # Check security data
        self.assertJENotExists(paths, '/authors.get.security')
        self.assertJEExists(paths, '/private/authors.get.security')
        security = self.get_val(paths, '/private/authors.get.security')
        self.assertIn(dict(BearerAuth=[]), security)

        # Check a inherited get with default description
        get = self.get_val(paths, '/authors/{pk}.get')
        self.assertJE(get, 'summary', "Get author")
        # See comment in pfx/pfxcore/views/parameters/groups.py
        # self.assertJE(get, 'parameters.@0', {
        #     '$ref': "#/components/parameters/DateFormat"})
        self.assertJE(get, 'parameters.@0.in', "path")
        self.assertJE(get, 'parameters.@0.name', "pk")
        self.assertJE(get, 'parameters.@0.schema.type', "integer")
        self.assertJE(get, 'parameters.@0.required', True)
        self.assertJE(get, 'parameters.@0.description', "the author pk")
        # Check a inherited get with custom description
        self.assertJE(
            paths, '/authors-annotate/{pk}.get.summary',
            "Get custom author")
        # Check a slug
        get = self.get_val(paths, '/authors/slug/{slug}.get')
        self.assertJE(get, 'summary', "Get author by slug")
        # See comment in pfx/pfxcore/views/parameters/groups.py
        # self.assertJE(get, 'parameters.@0', {
        #     '$ref': "#/components/parameters/DateFormat"})
        self.assertJE(get, 'parameters.@0.in', "path")
        self.assertJE(get, 'parameters.@0.name', "slug")
        self.assertJE(get, 'parameters.@0.schema.type', "string")
        self.assertJE(get, 'parameters.@0.required', True)
        self.assertJE(get, 'parameters.@0.description', "the author slug name")

        # Check list parameters with auto generated filters
        get = self.get_val(paths, '/authors.get')
        self.assertJIn(get, 'parameters', {
            '$ref': '#/components/parameters/ListCount'})
        self.assertJIn(get, 'parameters', {
            '$ref': '#/components/parameters/ListItems'})
        self.assertJIn(get, 'parameters', {
            '$ref': '#/components/parameters/ListSearch'})
        self.assertJIn(get, 'parameters', {
            '$ref': '#/components/parameters/ListOrder'})
        self.assertJIn(get, 'parameters', {
            '$ref': '#/components/parameters/Subset'})
        self.assertJIn(get, 'parameters', {
            '$ref': '#/components/parameters/SubsetPage'})
        self.assertJIn(get, 'parameters', {
            '$ref': '#/components/parameters/SubsetPageSize'})
        self.assertJIn(get, 'parameters', {
            '$ref': '#/components/parameters/SubsetPageSubset'})
        self.assertJIn(get, 'parameters', {
            '$ref': '#/components/parameters/SubsetOffset'})
        self.assertJIn(get, 'parameters', {
            '$ref': '#/components/parameters/ListCount'})
        self.assertJIn(get, 'parameters', {
            '$ref': '#/components/parameters/SubsetLimit'})
        self.assertJIn(get, 'parameters',     {
            "in": "query",
            "name": "science_fiction",
            "schema": {
                "type": "array",
                "default": [],
                "items": {
                    "type": "boolean"
                }
            },
            "description": "Filter by science fiction (or)"
        })
        self.assertJIn(get, 'parameters', {
            "in": "query",
            "name": "heroic_fantasy",
            "schema": {
                "type": "array",
                "default": [],
                "items": {
                    "type": "boolean"
                }
            },
            "description": "Filter by heroic fantasy (or)"
        })
        self.assertJIn(get, 'parameters', {
            "in": "query",
            "name": "types",
            "schema": {
                "type": "array",
                "default": [],
                "items": {
                    "type": "number"
                }
            },
            "description": "Filter by types (or)"
        })
        self.assertJIn(get, 'parameters', {
            "in": "query",
            "name": "last_name",
            "schema": {
                "type": "array",
                "default": [],
                "items": {
                    "type": "boolean"
                }
            },
            "description": "Filter by last name (or)"
        })
        self.assertJIn(get, 'parameters', {
            "in": "query",
            "name": "first_name",
            "schema": {
                "type": "array",
                "default": [],
                "items": {
                    "type": "string"
                }
            },
            "description": "Filter by first name (or)"
        })
        self.assertJIn(get, 'parameters', {
            "in": "query",
            "name": "gender",
            "schema": {
                "type": "array",
                "default": [],
                "items": {
                    "type": "string"
                }
            },
            "description": "Filter by gender (or)"
        })
        self.assertJIn(get, 'parameters', {
            "in": "query",
            "name": "last_name_choices",
            "schema": {
                "type": "array",
                "default": [],
                "items": {
                    "type": "string"
                }
            },
            "description": "Filter by tolkien or asimov (or)"
        })

        schema_key = self.get_val(
            paths,
            '/authors/{pk}.get.responses.200.content.application/json.schema'
        )['$ref'].split('/')[-1]
        self.assertIn("Author", schema_key)
        props = spec['components']['schemas'][schema_key]['properties']
        self.assertJE(props, 'first_name.type', 'string')
        # Check an @rest_property field (readonly)
        self.assertJE(props, 'name_length.type', 'number')
        self.assertJE(props, 'name_length.readonly', True)
        self.assertJE(props, 'gender.type', 'string')
        self.assertJE(props, 'gender.enum', ['male', 'female'])
        self.assertJE(props, 'types.type', 'array')
        self.assertJE(props, 'types.items.type', 'object')
        self.assertJE(props, 'created_at.type', 'string')
        self.assertJE(props, 'created_at.format', 'date')

        schema_key = self.get_val(
            paths,
            '/authors.get.responses.200.content.application/json.schema'
        )['$ref'].split('/')[-1]
        self.assertIn("Author", schema_key)
        props = spec['components']['schemas'][schema_key]['properties']
        self.assertJE(props, 'items.type', 'array')
        self.assertJE(props, 'items.items.format', 'Author')
        self.assertSize(props, 'items.items.properties', 6)
        props = self.get_val(props, 'items.items.properties')
        self.assertJE(props, 'pk.type', 'number')
        self.assertJE(props, 'resource_name.type', 'string')
        self.assertJE(props, 'resource_slug.type', 'string')
        self.assertJE(props, 'first_name.type', 'string')
        self.assertJE(props, 'first_name.readonly', False)
        self.assertJE(props, 'last_name.type', 'string')
        self.assertJE(props, 'last_name.readonly', False)
        self.assertJE(props, 'gender.type', 'string')
        self.assertJE(props, 'gender.enum', ['male', 'female'])

        schema_key = self.get_val(
            paths,
            '/authors-annotate/{pk}.get.responses.200.content'
            '.application/json.schema'
        )['$ref'].split('/')[-1]
        # Check ModelObjectList fields
        props = spec['components']['schemas'][schema_key]['properties']
        self.assertJE(props, 'books.type', 'array')
        self.assertJE(props, 'books.items.type', 'object')
        self.assertJE(props, 'books.items.format', 'Book')
        props = self.get_val(props, 'books.items.properties')
        self.assertJE(props, 'pk.type', 'number')
        self.assertJE(props, 'resource_name.type', 'string')
        self.assertJE(props, 'resource_reference.type', 'string')
        self.assertJE(props, 'author_name.type', 'string')
        self.assertJE(props, 'author_gender.type', 'string')

        schema_key = self.get_val(
            paths,
            '/books-custom-author/{pk}.get.responses.200.content'
            '.application/json.schema'
        )['$ref'].split('/')[-1]
        self.assertIn("Book", schema_key)
        props = spec['components']['schemas'][schema_key]['properties']
        # Check VF field with alias
        self.assertJE(props, 'book_name.type', 'string')
        self.assertJE(props, 'book_name.readonly', False)
        # Check VF field with django lookup (author__last_name)
        self.assertJE(props, 'author_last_name.type', 'string')
        self.assertJE(props, 'author_last_name.readonly', True)
        # Check that json_repr docstring from VF is used
        self.assertJE(props, 'author.properties.hello.type', 'string')
        self.assertJE(props, 'author.properties.last_name.type', 'string')

        schema_key = self.get_val(
            paths,
            '/books/{pk}.get.responses.200.content.application/json.schema'
        )['$ref'].split('/')[-1]
        self.assertIn("Book", schema_key)
        props = spec['components']['schemas'][schema_key]['properties']
        # Check that json_repr docstring from model is used
        self.assertJE(props, 'author.properties.new_field.type', 'string')
        # Check MinutesDurationField fields json schema
        self.assertJE(props, 'read_time.type', 'object')
        self.assertJE(props, 'read_time.properties.minutes.type', 'number')
        self.assertJE(
            props, 'read_time.properties.clock_format.type', 'string')
        self.assertJE(
            props, 'read_time.properties.human_format.type', 'string')

        schema_key = self.get_val(
            paths,
            '/books/meta.get.responses.200.content.application/json.schema'
        )['$ref'].split('/')[-1]
        self.assertIn("form_meta", schema_key)
        props = spec['components']['schemas'][schema_key]['properties']
        # Check that schema contains fields
        self.assertJE(props, 'fields.type', 'array')

        schema_key = self.get_val(
            paths,
            '/books/meta/list.get.responses.200.content'
            '.application/json.schema'
        )['$ref'].split('/')[-1]
        self.assertIn("list_meta", schema_key)
        props = spec['components']['schemas'][schema_key]['properties']
        # Check that schema contains fields+filters+orders
        self.assertJE(props, 'fields.type', 'array')
        self.assertJE(props, 'filters.type', 'array')
        self.assertJE(props, 'orders.type', 'array')

        schema_key = self.get_val(
            paths,
            '/books.post.requestBody.content.application/json.schema'
        )['$ref'].split('/')[-1]
        self.assertIn("Book", schema_key)
        props = spec['components']['schemas'][schema_key]['properties']
        # Check readonly is not in schema
        self.assertJENotExists(props, 'created_at')
        # Check foreign object can be number/object
        self.assertJE(props, 'author.oneOf.@0.type', 'number')
        self.assertJE(props, 'author.oneOf.@1.type', 'object')
        self.assertSize(props, 'author.oneOf.@1.properties', 1)
        self.assertJE(props, 'author.oneOf.@1.properties.pk.type', 'number')

    def test_paths_order(self):
        spec = get_spec(set()).to_dict()
        paths = self.get_val(spec, 'paths')
        authors_paths = [p for p in paths if p.startswith('/authors')]
        self.assertEqual(authors_paths[:11], [
            '/authors',
            '/authors/{pk}',
            '/authors/slug/{slug}',
            '/authors/cache/{pk}',
            '/authors/priority/{value}',
            '/authors/priority/default',
            '/authors/priority/default/path',
            '/authors/priority/priority-less',
            '/authors/priority/priority-more',
            '/authors/meta/list',
            '/authors/meta'])
        books_paths = [p for p in paths if p.startswith('/books')]
        self.assertEqual(books_paths, [
            "/books",
            "/books/{pk}",
            "/books/{pk}/{field}",
            "/books/{pk}/{field}/upload-url/{filename}",
            "/books/meta/list",
            "/books/meta",
            "/books-custom-author",
            "/books-custom-author/{pk}",
            "/books-custom-author/{pk}/{field}",
            "/books-custom-author/{pk}/{field}/upload-url/{filename}",
            "/books-custom-author/meta/list",
            "/books-custom-author/meta"])

    def test_groups(self):
        spec = get_spec(set()).to_dict()
        self.assertJEExists(spec, 'paths./authors/cache/{pk}.get')
        self.assertJEExists(spec, 'paths./authors-annotate/{pk}.get')

        spec = get_spec({'cache', }).to_dict()
        self.assertJEExists(spec, 'paths./authors/cache/{pk}.get')
        self.assertJENotExists(spec, 'paths./authors-annotate/{pk}.get')

        spec = get_spec({'custom', }).to_dict()
        self.assertJENotExists(spec, 'paths./authors/cache/{pk}.get')
        self.assertJEExists(spec, 'paths./authors-annotate/{pk}.get')

        spec = get_spec({'cache', 'custom'}).to_dict()
        self.assertJEExists(spec, 'paths./authors/cache/{pk}.get')
        self.assertJEExists(spec, 'paths./authors-annotate/{pk}.get')

        spec = get_spec({'default', }).to_dict()
        self.assertJENotExists(spec, 'paths./authors/cache/{pk}.get')
        self.assertJENotExists(spec, 'paths./authors-annotate/{pk}.get')

    def test_view_get_urls(self):
        def assertMethods(urls, p, methods):
            self.assertEqual(next(filter(
                lambda u: u['path'] == p, urls))['methods'], methods)

        urls = AuthorRestView.get_urls()

        # Methods from RestView
        assertMethods(urls, '/authors', dict(get='get_list', post='post'))
        assertMethods(urls, '/authors/<int:id>', dict(
            delete='delete', get='get', put='put'))
        # A method from SlugDetailRestViewMixin
        assertMethods(urls, '/authors/slug/<slug:slug>', dict(
            get='get_by_slug'))
        # A method from AuthorRestView itself
        assertMethods(urls, '/authors/cache/<int:id>', dict(get='cache_get'))

    def test_path_parameter_untyped(self):
        param = next(path_parameters(from_doc(""), '/path/<my_param>'))
        self.assertJE(param, 'in', "path")
        self.assertJE(param, 'name', "my_param")
        self.assertJE(param, 'schema.type', "string")
        self.assertJE(param, 'required', True)
        self.assertJENotExists(param, 'description')

    def test_path_parameter_str(self):
        param = next(path_parameters(from_doc(""), '/path/<str:my_param>'))
        self.assertJE(param, 'in', "path")
        self.assertJE(param, 'name', "my_param")
        self.assertJE(param, 'schema.type', "string")
        self.assertJE(param, 'required', True)
        self.assertJENotExists(param, 'description')

    def test_path_parameter_int(self):
        param = next(path_parameters(from_doc(""), '/path/<int:my_param>'))
        self.assertJE(param, 'in', "path")
        self.assertJE(param, 'name', "my_param")
        self.assertJE(param, 'schema.type', "integer")
        self.assertJE(param, 'required', True)
        self.assertJENotExists(param, 'description')

    def test_path_parameter_slug(self):
        param = next(path_parameters(from_doc(""), '/path/<slug:my_param>'))
        self.assertJE(param, 'in', "path")
        self.assertJE(param, 'name', "my_param")
        self.assertJE(param, 'schema.type', "string")
        self.assertJE(param, 'required', True)
        self.assertJENotExists(param, 'description')

    def test_path_parameter_uuid(self):
        param = next(path_parameters(from_doc(""), '/path/<uuid:my_param>'))
        self.assertJE(param, 'in', "path")
        self.assertJE(param, 'name', "my_param")
        self.assertJE(param, 'schema.type', "string")
        self.assertJE(param, 'required', True)
        self.assertJENotExists(param, 'description')

    def test_path_parameter_path(self):
        param = next(path_parameters(from_doc(""), '/path/<path:my_param>'))
        self.assertJE(param, 'in', "path")
        self.assertJE(param, 'name', "my_param")
        self.assertJE(param, 'schema.type', "string")
        self.assertJE(param, 'required', True)
        self.assertJENotExists(param, 'description')

    def test_path_parameter_custom(self):
        """Test with a custom path type.
        Actually you cannot register your custom path type. Every custom
        type will be considered as string."""
        param = next(path_parameters(from_doc(""), '/path/<custom:my_param>'))
        self.assertJE(param, 'in', "path")
        self.assertJE(param, 'name', "my_param")
        self.assertJE(param, 'schema.type', "string")
        self.assertJE(param, 'required', True)
        self.assertJENotExists(param, 'description')

    def test_path_parameter_description(self):
        param = next(path_parameters(from_doc(
            """Test
            ---
            get:
                parameters extras:
                    my_param: a test description
            """).get('get'), '/path/<my_param>'))
        self.assertJE(param, 'in', "path")
        self.assertJE(param, 'name', "my_param")
        self.assertJE(param, 'schema.type', "string")
        self.assertJE(param, 'required', True)
        self.assertJE(param, 'description', 'a test description')

    def test_path_parameter_extras(self):
        param = next(path_parameters(from_doc(
            """Test
            ---
            get:
                parameters extras:
                    my_param:
                        description: a test description
                        schema:
                            type: number
            """).get('get'), '/path/<my_param>'))
        self.assertJE(param, 'in', "path")
        self.assertJE(param, 'name', "my_param")
        self.assertJE(param, 'schema.type', "number")
        self.assertJE(param, 'required', True)
        self.assertJE(param, 'description', 'a test description')

    def test_make_api_doc(self):
        out = StringIO()
        call_command("makeapidoc", stdout=out)
        self.assertIn(
            "OpenAPI documentation generated: doc/api/openapi.json",
            out.getvalue())
        call_command("makeapidoc", '--format=yaml', stdout=out)
        self.assertIn(
            "OpenAPI documentation generated: doc/api/openapi.yaml",
            out.getvalue())
