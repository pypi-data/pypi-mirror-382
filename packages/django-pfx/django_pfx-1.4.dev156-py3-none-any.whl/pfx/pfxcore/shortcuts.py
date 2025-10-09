
import logging
from datetime import date
from decimal import Decimal as D

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from .settings import settings

logger = logging.getLogger(__name__)


def f(tmpl, **kwargs):
    return tmpl.format(**kwargs)


def get_object(queryset, related_field=None, **kwargs):
    from .exceptions import ModelNotFoundAPIError, RelatedModelNotFoundAPIError
    try:
        return queryset.get(**kwargs)
    except ObjectDoesNotExist:
        if related_field:
            raise RelatedModelNotFoundAPIError(related_field, queryset.model)
        raise ModelNotFoundAPIError(queryset.model)


def get_pk(obj):
    if isinstance(obj, dict) and 'pk' in obj:
        return obj['pk']
    return obj


def is_null(value):
    return not value or value.lower() in ('null', 'undefined')


def parse_int(value):
    if is_null(value):
        return None
    return int(value)


def get_int(data, key, default=None):
    if key not in data:
        return default
    try:
        return parse_int(data.get(key))
    except ValueError:
        from pfx.pfxcore.exceptions import APIError
        raise APIError(f(_("{key} must be an integer number."), key=key))


def parse_float(value):
    if is_null(value):
        return None
    return float(value)


def get_float(data, key, default=None):
    if key not in data:
        return default
    try:
        return parse_float(data.get(key))
    except ValueError:
        from pfx.pfxcore.exceptions import APIError
        raise APIError(f(_("{key} must be a number."), key=key))


def parse_decimal(value):
    if is_null(value):
        return None
    return D(value)


def get_decimal(data, key, default=None):
    if key not in data:
        return default
    try:
        return parse_decimal(data.get(key))
    except Exception:
        from pfx.pfxcore.exceptions import APIError
        raise APIError(f(_("{key} must be a decimal number."), key=key))


def parse_date(value):
    if is_null(value):
        return None
    return date.fromisoformat(value)


def get_date(data, key, default=None):
    if key not in data:
        return default
    try:
        return parse_date(data.get(key))
    except ValueError:
        from pfx.pfxcore.exceptions import APIError
        raise APIError(f(_("{key} must be a date."), key=key))


def parse_bool(value):
    if is_null(value):
        return None
    if value.lower() in ('true', '1'):
        return True
    if value.lower() in ('false', '0'):
        return False
    raise ValueError(f"{value} is not a valid boolean value.")


def get_bool(data, key, default=None):
    if key not in data:
        return default
    try:
        return parse_bool(data.get(key))
    except ValueError:
        from pfx.pfxcore.exceptions import APIError
        raise APIError(f(
            _("{key} must be “true”, “false”, “1”, “0” or empty."),
            key=key))


def delete_token_cookie(response):
    response.delete_cookie(
        'token',
        domain=settings.PFX_COOKIE_DOMAIN,
        samesite=settings.PFX_COOKIE_SAMESITE)
    return response


def register_views(*views):
    def _register():
        for v in views:
            yield from v.as_urlpatterns()
    return list(_register())


def class_key(cls, *args):
    return f"{cls.__module__}.{cls.__name__}{''.join(f'.{a}' for a in args)}"


def permissions(*perms):
    from django.contrib.auth.models import Permission
    pks = set()
    for perm in perms:
        app_label, codename = perm.split('.')
        try:
            pks.add(Permission.objects.get(
                codename=codename, content_type__app_label=app_label).pk)
        except Permission.DoesNotExist:
            raise Exception(f"Permission {perm} does not exists.")
    return Permission.objects.filter(pk__in=pks)


def model_permissions(model, *actions):
    meta = model._meta
    return {f"{meta.app_label}.{a}_{meta.model_name}" for a in actions}
