from functools import reduce

from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from pfx.pfxcore.exceptions import APIError
from pfx.pfxcore.shortcuts import (
    f,
    parse_bool,
    parse_date,
    parse_float,
    parse_int,
)
from pfx.pfxcore.views import FieldType


class FilterGroup():
    def __init__(self, name, label, filters):
        self.name = name
        self.label = label
        self.filters = filters

    @property
    def meta(self):
        return dict(is_group=True, name=self.name, label=self.label, items=[
            f.meta for f in self.filters
        ])

    def query(self, params):
        return Q(*[f.query(params) for f in self.filters])


class Filter():
    def __init__(
            self, name, label, type=None, filter_func=None,
            filter_func_and=False, filter_func_list=False, choices=None,
            related_model=None, related_model_api=None,
            technical=False, defaults=None, empty_value=True):
        self.name = name
        self.label = label
        self.type = type
        self.filter_func = filter_func
        self.filter_func_and = filter_func_and
        self.filter_func_list = filter_func_list
        self.choices = choices
        self.related_model = related_model
        self.related_model_api = related_model_api
        self.technical = technical
        self.defaults = defaults or []
        self.empty_value = empty_value

    @property
    def meta(self):
        res = dict(
            is_group=False,
            label=_(self.label),
            name=self.name,
            type=self.type,
            empty_value=self.empty_value,
            technical=self.technical)
        if self.choices:
            res['choices'] = [
                dict(label=_(v), value=k) for k, v in self.choices]
        if self.related_model:
            res['related_model'] = str(self.related_model.__name__)
            res['api'] = self.related_model_api
        return res

    def _parse_value(self, value):
        try:
            if self.type == FieldType.BooleanField:
                return parse_bool(value)
            if self.type in (FieldType.IntegerField, FieldType.ModelObject):
                return parse_int(value)
            if self.type == FieldType.FloatField:
                return parse_float(value)
            if self.type == FieldType.DateField:
                return parse_date(value)
        except ValueError:
            raise APIError(f(
                _("Invalid value for {filter} filter"), filter=self.label))
        return value

    def _call_filter_func(self, values):
        if self.filter_func_list:
            return self.filter_func(values)
        return reduce(
            lambda x, y: x & y if self.filter_func_and else x | y,
            [self.filter_func(v) for v in values])

    def _get_values(self, params):
        values = []
        if (self.type == FieldType.ModelObject and self.related_model and
                hasattr(self.related_model.objects, 'default_search')):
            q = None
            for search in params.getlist(f'{self.name}*'):
                crit = self.related_model.objects.default_search(search)
                if q is None:
                    q = crit
                q |= crit
            if q:
                values.extend(self.related_model.objects.filter(
                    q).values_list('pk', flat=True) or [-1])
        values.extend([
            self._parse_value(v) for v in params.getlist(self.name)])
        return values or self.defaults

    def query(self, params):
        values = self._get_values(params)
        return self._call_filter_func(values) if values else Q()


class ModelFilter(Filter):
    def __init__(
            self, model, name, label=None, type=None,
            filter_func=None, filter_func_and=False, filter_func_list=False,
            choices=None, related_model=None, related_model_api=None,
            technical=False, defaults=None, empty_value=None):
        self.model = model
        self.field = model._meta.get_field(name)
        if empty_value is None:
            empty_value = self.field.blank
        super().__init__(
            name, label or self.field.verbose_name,
            type or self._type_from_model,
            filter_func, filter_func_and, filter_func_list,
            choices or self.field.choices,
            related_model or (
                self.field.remote_field and
                self.field.remote_field.model),
            related_model_api or (
                self.field.remote_field and
                self.field.remote_field.model and
                hasattr(self.field.remote_field.model, 'api') and
                self.field.remote_field.model.api),
            technical=technical, defaults=defaults, empty_value=empty_value)

    @property
    def _type_from_model(self):
        model_type = FieldType.from_model_field(self.field.__class__)
        if model_type == FieldType.ModelObjectList:
            # For list related fields (OneToMany, ManyToMany, …) the field
            # type is ModelObjectList, but the filter type should be
            # ModelObject.
            return FieldType.ModelObject
        return model_type

    def query(self, params):
        values = self._get_values(params)
        if self.filter_func and values:
            return self._call_filter_func(values)
        elif values:
            return reduce(
                lambda x, y: x & y if self.filter_func_and else x | y,
                [Q(**{self.name: v}) for v in values])
        return Q()
