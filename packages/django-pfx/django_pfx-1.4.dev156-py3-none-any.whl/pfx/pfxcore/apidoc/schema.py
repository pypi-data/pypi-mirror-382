import json
from hashlib import sha1

from apispec.utils import deepupdate


class Schema:
    def __init__(self, id, name, **kwargs):
        self._id = id
        self._name = name
        self._kwargs = kwargs

    def id(self):
        hash = sha1(json.dumps(self.to_schema()).encode()).hexdigest()[:10]
        return f"{self._id}.{hash}"

    def to_ref(self, schema=False):
        return {
            'description': self._name,
            'content': {'application/json': {'schema':
                        schema and self.to_schema() or self.id()}}}

    def to_schema(self):
        return dict(**self._kwargs)


class ModelSchema(Schema):
    def __init__(self, model, fields, properties=None, mode=None):
        self.model = model
        self.fields = fields
        self._properties = properties
        self._mode = mode

    def id(self):
        hash = sha1(json.dumps(self.to_schema()).encode()).hexdigest()[:10]
        return f"{self.model.__name__}.{hash}"

    def to_ref(self, schema=False):
        return {
            'description': str(self.model._meta.verbose_name),
            'content': {'application/json': {'schema':
                        schema and self.to_schema() or self.id()}}}

    def default_json_repr_schema(self):
        from pfx.pfxcore.views.fields import FieldType
        return dict(
            pk=dict(
                type=FieldType.to_apidoc(FieldType.from_model_field(
                    self.model._meta.pk.__class__)),
                readonly=True),
            resource_name=dict(type='string', readonly=True))

    def to_schema(self):
        if self._mode in ('create', 'update'):
            properties = {}
        else:
            properties = getattr(
                self.model, 'json_repr_schema',
                self.default_json_repr_schema)()
        for name, field in self.fields.items():
            if self._mode == 'create' and field.readonly_create:
                continue
            if self._mode == 'update' and field.readonly_update:
                continue
            doc = (
                hasattr(self.model, 'apidoc') and
                self.model.apidoc.get(field.name) or {})
            properties[name] = deepupdate(
                field.to_apidoc(
                    self._mode in ('create', 'update')), doc.copy())
        if self._properties:
            properties.update(self._properties)
        return dict(properties=properties)


class ModelListSchema(ModelSchema):
    def to_ref(self, schema=False):
        return {
            'description': str(self.model._meta.verbose_name_plural),
            'content': {'application/json': {'schema':
                        schema and self.to_schema() or self.id()}}}

    def to_schema(self):
        model = super().to_schema()
        return dict(properties=dict(
            items=dict(type='array', items=dict(
                type='object', format=str(self.model._meta.verbose_name),
                **model)),
            meta=dict(type='object')))
