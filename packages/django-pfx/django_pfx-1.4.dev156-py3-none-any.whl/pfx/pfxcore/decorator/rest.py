import logging
from functools import wraps

from django.utils.translation import gettext_lazy as _

from apispec.utils import deepupdate

from pfx.pfxcore.exceptions import APIError
from pfx.pfxcore.http import JsonResponse
from pfx.pfxcore.settings import settings
from pfx.pfxcore.test import format_request

logger = logging.getLogger(__name__)


def rest_api(
        path, method='get', public=None, perms=None,
        priority=0, priority_doc=0, parameters=None,
        request_schema=None, response_schema=None, filters=False,
        search=False, groups=None):
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            self.request = request
            self.kwargs = kwargs
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("")
                logger.debug("##### REQUEST %s #####", request)
                logger.debug("")
            if (settings.PFX_TEST_MODE and
                    'HTTP_X_PRINT_REQUEST' in request.META):
                print(format_request(request))
            try:
                self.check_perm(public, func.__name__, perms, *args, **kwargs)
                return func(self, *args, **kwargs)
            except APIError as e:
                return e.response
            except Exception as e:
                logger.exception(e)
                return JsonResponse(dict(message=_(
                    "An internal server error occured.")), status=500)
        wrapper.rest_api_path = path
        wrapper.rest_api_method = method
        wrapper.rest_api_priority = priority
        wrapper.rest_api_priority_doc = priority_doc
        wrapper.rest_api_params = parameters or []
        wrapper.rest_api_request_schema = request_schema
        wrapper.rest_api_response_schema = response_schema
        wrapper.rest_api_filters = filters
        wrapper.rest_api_search = search
        wrapper.rest_api_groups = set(groups or [])
        wrapper.rest_api_public = public
        return wrapper
    return decorator


def rest_property(string=None, type="CharField", field=None, order=None):
    def decorator(func):
        func.short_description = string
        func.field_type = type
        func.field = field
        func.order = order
        return property(func)
    return decorator


def rest_view(path):
    def decorator(cls):
        cls.rest_view_path[cls] = path
        cls._rest_view_path = path
        return cls
    return decorator


def rest_doc(path, method, priority=None, **vals):
    def decorator(cls):
        if cls not in cls.rest_view_path:
            raise Exception(
                "@rest_doc must be used before a @rest_view decorator")
        key = f'{cls.rest_view_path[cls]}{path}', method
        cls.rest_doc[key] = deepupdate(cls.rest_doc.get(key, {}), vals)
        if priority is not None:
            cls.rest_doc_priority[key] = priority
        return cls
    return decorator
