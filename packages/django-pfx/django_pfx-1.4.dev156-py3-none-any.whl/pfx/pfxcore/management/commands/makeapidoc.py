import inspect
import json
import re
from pathlib import Path

from django.core.management.base import BaseCommand

from apispec import APISpec
from apispec.utils import deepupdate
from apispec.yaml_utils import load_operations_from_docstring

from pfx.pfxcore import __PFX_VIEWS__
from pfx.pfxcore.apidoc import __PARAMETERS__, __TAGS__, ParameterGroup
from pfx.pfxcore.settings import settings
from pfx.pfxcore.views import FilterGroup, ModelMixin

DEFAULT_TEMPLATE = dict(
    title="PFX API",
    version="1.0.0",
    openapi_version="3.0.2")
RE_PATH_PARAMS = re.compile(r'<(?:(\w+):)?(\w+)>')
DJANGO_OPENAPI_TYPES = {
    'str': 'string',
    'int': 'integer',
    'slug': 'string',
    'uuid': 'string',
    'path': 'string',
}


def from_django_path(path):
    return RE_PATH_PARAMS.sub(r'{\g<2>}', path)


def path_parameters(spec, path):
    def as_dict(data):
        return data if isinstance(data, dict) else dict(description=data)

    existings = {
        p.get('name', '#N/A') for p in spec.get('parameters', [])
        if isinstance(p, dict)}
    extras = spec.pop('parameters extras', {}).copy()
    for ptype, name in RE_PATH_PARAMS.findall(path):
        if name in existings:
            # Ignore path parameters that are manually described.
            continue
        yield deepupdate({
            'in': 'path',
            'name': name,
            'schema': {'type': DJANGO_OPENAPI_TYPES.get(ptype, 'string')},
            'required': True}, as_dict(extras.get(name, {})))


def global_parameters(spec, method):
    def extend_groups(params):
        for p in params:
            if issubclass(p, ParameterGroup):
                yield from p.parameters
            else:
                yield p

    existings = {
        p.get('name', '#N/A') for p in spec.get('parameters', [])
        if isinstance(p, dict)}
    for qp in extend_groups(method.rest_api_params):
        if qp.name == 'search':
            search = (
                spec['search'] if 'search' in spec else method.rest_api_search)
            if not search:
                continue
            if isinstance(search, str):
                yield qp.as_parameter(doc=search)
                continue
        if qp.name in existings:
            # Ignore path parameters that are manually described.
            continue
        yield qp.id()


def filters_parameters(view):
    def get_filters(src):
        if not hasattr(src, 'filters'):
            return
        for e in src.filters:
            if isinstance(e, FilterGroup):
                yield from get_filters(e)
            else:
                yield e

    from pfx.pfxcore.views.fields import FieldType
    for f in get_filters(view):
        if f.type == FieldType.ModelObject and f.related_model:
            ftype = FieldType.from_model_field(
                f.related_model._meta.pk.__class__)
        else:
            ftype = f.type
        op = (
            not f.filter_func_list and
            f" ({f.filter_func_and and 'and' or 'or'})" or "")
        yield {
            'in': 'query',
            'name': str(f.name),
            'schema': dict(
                type='array', default=f.defaults,
                items=dict(type=FieldType.to_apidoc(ftype))),
            'description': f"Filter by {f.label.lower()}{op}"}


def get_operations(view, url, auths, groups):
    order = dict(get=1, post=2, put=3, delete=4)
    for op, method_name in sorted(
            url['methods'].items(), key=lambda e: order.get(e[0], 99)):
        method = getattr(view, method_name)
        rest_doc = view.rest_doc.get((url['path'], op), {}).copy()
        rest_groups = (
            (method.rest_api_groups | set(rest_doc.pop('groups', []))) or
            {'default', })
        if groups and not (groups & rest_groups):
            continue
        doc = inspect.getdoc(method)
        vars = {}
        if issubclass(view, ModelMixin) and view.model:
            vars.update(
                model=view.model._meta.verbose_name.lower(),
                models=view.model._meta.verbose_name_plural.lower())
        if doc:
            doc = doc.format(**vars)
        spec = deepupdate(
            load_operations_from_docstring(doc).get(op, {}), rest_doc)
        if auths and not view()._is_public(
                method.rest_api_public, method_name):
            # If not public, add all defined security schemes
            for a in auths:
                spec.setdefault('security', []).append({a: []})
        spec.setdefault('summary', from_django_path(url['fixed_path']))
        tags = view.get_apidoc_tags()
        tags_d = {}
        for tag in tags:
            tags_d[tag.name] = tag
        spec.setdefault('tags', list(tags_d.keys()))
        __TAGS__.update(tags_d)
        parameters = spec.setdefault('parameters', [])
        parameters.extend(global_parameters(spec, method))
        parameters.extend(path_parameters(spec, url['path']))
        if method.rest_api_filters:
            parameters.extend(filters_parameters(view))
        for p in parameters:
            if 'name' in p and p['name'] == 'id':
                p['name'] = 'pk'
        if method.rest_api_request_schema:
            schema = getattr(view, method.rest_api_request_schema)
            spec_schema = spec.setdefault('requestBody', {})
            if spec_schema:
                spec_schema.update(deepupdate(
                    schema.to_ref(schema=True),
                    spec_schema.copy()))
            else:
                spec_schema.update(schema.to_ref())
        if method.rest_api_response_schema:
            schema = getattr(view, method.rest_api_response_schema)
            spec_schema = spec.setdefault('responses', {}).setdefault(200, {})
            if spec_schema:
                spec_schema.update(deepupdate(
                    schema.to_ref(schema=True), spec_schema.copy()))
            else:
                spec_schema.update(schema.to_ref())
        yield op, spec


def get_spec(groups):
    re_pk = re.compile(r'<(\w+:)?id>')
    spec = APISpec(**{**DEFAULT_TEMPLATE, **settings.PFX_OPENAPI_TEMPLATE})
    auths = spec.to_dict().get(
        'components', {}).get('securitySchemes', {}).keys()
    for parameter in __PARAMETERS__:
        spec.components.parameter(
            parameter.id(), parameter.location, parameter.as_parameter())
    for view in __PFX_VIEWS__:
        view.generate_schemas()
        for schema in view.get_apidoc_schemas():
            if schema.id() not in spec.components.schemas:
                spec.components.schema(schema.id(), schema.to_schema())
        for url in view.get_urls():
            url['fixed_path'] = re_pk.sub(r'<\g<1>pk>', url['path'])
            spec.path(
                path=from_django_path(url['fixed_path']),
                operations=dict(get_operations(view, url, auths, groups)))
    for key in sorted(__TAGS__.keys()):
        spec.tag(__TAGS__[key].to_dict())

    # If application use x-tagGroups, remove groups without exported tags:
    tag_groups = spec.options.get('x-tagGroups')
    if tag_groups:
        spec.options['x-tagGroups'] = list(filter(
            lambda tg: set(tg.get('tags', [])) & set(__TAGS__.keys()),
            tag_groups))
    return spec


class Command(BaseCommand):
    help = 'Generate OpenAPI documentation'

    def add_arguments(self, parser):
        parser.add_argument("groups", nargs="*", type=str)
        parser.add_argument(
            "-f", "--format", dest="format", choices=['json', 'yaml'],
            default="json", type=str)

    def handle(self, *args, groups=None, **options):
        spec = get_spec(set(groups))

        path = Path(
            settings.PFX_OPENAPI_PATH,
            f'{settings.PFX_OPENAPI_FILENAME}.{options["format"]}')
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as outfile:
            if options["format"] == 'yaml':
                outfile.write(spec.to_yaml())
            else:
                json.dump(spec.to_dict(), outfile, indent=2)

        self.stdout.write(self.style.SUCCESS(
            f"OpenAPI documentation generated: {path}"))
