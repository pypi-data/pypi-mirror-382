import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import translation
from django.utils.cache import patch_vary_headers
from django.utils.deprecation import MiddlewareMixin

import pytz

logger = logging.getLogger(__name__)


def get_language_from_request(request):
    """Custom version of django `get_language_from_request` from translation.

    Remove path and cookies parsing and just use `X-Custom-language` as
    first choice if it is defined and valid, then use `Accept-Language`.

    :param request: The HTTP request.
    :type request: HttpRequest
    :return: The language code.
    :rtype: str
    """
    _trans = translation._trans  # Load _trans dynamically from translation.

    x_custom_language = request.META.get('HTTP_X_CUSTOM_LANGUAGE', '')
    custom_lang = translation.to_language(x_custom_language)
    try:
        return _trans.get_supported_language_variant(custom_lang)
    except LookupError:
        logger.debug(
            "Unsupported x-custom-language header: "
            f"{x_custom_language} [lang={custom_lang}]")
        pass

    accept = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    for accept_lang, unused in _trans.parse_accept_lang_header(accept):
        if accept_lang == '*':
            break  # pragma: no cover
        if not _trans.language_code_re.search(accept_lang):
            continue  # pragma: no cover
        try:
            return _trans.get_supported_language_variant(accept_lang)
        except LookupError:
            logger.debug(
                f"Unsupported accept-language header: {accept}]")
            continue

    try:
        return _trans.get_supported_language_variant(settings.LANGUAGE_CODE)
    except LookupError:  # pragma: no cover
        logger.debug(
            f"Unsupported LANGUAGE_CODE: {settings.LANGUAGE_CODE}]")
        return settings.LANGUAGE_CODE


def get_timezone_from_request(request):
    """Get the timezone from request.

    If `X-Custom-Timezone` is defined in request headers and is valid (exists
    in `pytz.all_timezones_set`), it is returned. Otherwise, the default
    timezone (from DJango) is returned.

    :param request: The HTTP request.
    :type request: HttpRequest
    :return: The request timezone.
    :rtype: str
    """
    default_tz = getattr(settings, "TIME_ZONE", "UTC")
    tz = request.META.get('HTTP_X_CUSTOM_TIMEZONE', default_tz)
    if tz not in pytz.all_timezones_set:
        return default_tz
    return tz


class LocaleMiddleware(MiddlewareMixin):
    """A middleware to load locale data from request.

    * `request.LANGUAGE_CODE` is set from `get_language_from_request`.
    * `request.TIMEZONE` is set from `get_timezone_from_request`.
    * `Content-Language` is set in the response headers to specify the used
      language.
    """
    response_redirect_class = HttpResponseRedirect

    def process_request(self, request):
        language = get_language_from_request(request)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
        request.TIMEZONE = get_timezone_from_request(request)

    def process_response(self, request, response):
        patch_vary_headers(response, ('Accept-Language',))
        code = (
            len(request.LANGUAGE_CODE) == 5 and
            request.LANGUAGE_CODE[:3] + request.LANGUAGE_CODE[-2:].upper() or
            request.LANGUAGE_CODE)
        response.headers.setdefault('Content-Language', code)
        return response
