import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin

import jwt
from jwt import DecodeError

from pfx.pfxcore.models import CacheableMixin
from pfx.pfxcore.shortcuts import delete_token_cookie

logger = logging.getLogger(__name__)


class JWTTokenDecodeMixin:

    @classmethod
    def get_cached_user(cls, pk):
        UserModel = get_user_model()
        has_cache = issubclass(UserModel, CacheableMixin)
        if (has_cache):
            user = UserModel.cache_get(pk)
            if user:
                return user
        user = UserModel._default_manager.get(pk=pk)
        if (has_cache):
            user.cache()
        return user

    @classmethod
    def decode_jwt_header(cls, token):
        try:
            headers = jwt.get_unverified_header(token)
            if 'pfx_user_pk' not in headers:
                raise jwt.InvalidTokenError(
                    "Missing pfx_user_pk in token headers")
            return headers['pfx_user_pk']
        except (jwt.ExpiredSignatureError,
                jwt.InvalidTokenError, jwt.InvalidSignatureError,
                DecodeError) as e:
            # Log these exceptions only in debug mode
            logger.debug(e, exc_info=True)
            raise
        except Exception as e:
            # Always logs unexpected exceptions
            logger.exception(e)
            raise

    @classmethod
    def decode_jwt(cls, token, otp_login=False):
        user_pk = cls.decode_jwt_header(token)
        try:
            user = cls.get_cached_user(user_pk)
            decoded = jwt.decode(
                token,
                user.get_user_jwt_signature_key() + settings.PFX_SECRET_KEY,
                options=dict(require=["exp"]),
                algorithms="HS256")
            if decoded.get('pfx_otp_login') and not otp_login:
                raise jwt.InvalidTokenError(
                    "This token is reserved for OTP login")
            return user, *decoded.get('pfx_login_options', ['jwt', False])
        except (get_user_model().DoesNotExist, jwt.ExpiredSignatureError,
                jwt.InvalidTokenError, jwt.InvalidSignatureError,
                DecodeError) as e:
            # Log these exceptions only in debug mode
            logger.debug(e, exc_info=True)
            raise
        except Exception as e:
            # Always logs unexpected exceptions
            logger.exception(e)
            raise


class AuthenticationMiddleware(JWTTokenDecodeMixin, MiddlewareMixin):
    """A middleware to authenticate with a bearer token.

    If `Authorization` is defined in request headers and the value is
    a valid JWT token (in the `"Bearer $TOKEN"` format), use it to
    set `request.user`. Otherwise, set it with
    `django.contrib.auth.models.AnonymousUser()`.
    """

    def process_request(self, request):
        authorization = request.headers.get('Authorization')
        if authorization:
            try:
                _, token = authorization.split("Bearer ")
            except ValueError:
                token = ""
            try:
                request.user, request.login_mode, request.login_remember_me = (
                    self.decode_jwt(token))
            except Exception:
                request.user = AnonymousUser()
        else:
            if not hasattr(request, 'user'):
                request.user = AnonymousUser()

    def process_response(self, request, response):
        return response


class CookieAuthenticationMiddleware(JWTTokenDecodeMixin, MiddlewareMixin):
    """A middleware to authenticate with a cookie.

    If `token` is defined in cookies and the value is
    a valid JWT token, use it to set `request.user`.
    Otherwise, set it with
    `django.contrib.auth.models.AnonymousUser()`.

    If the token is not valid, delete the cookie.

    If `request.delete_cookie` is `True` after the processing,
    delete the cookie.
    """

    def process_request(self, request):
        token = request.COOKIES.get('token', "")
        if token:
            try:
                request.user, request.login_mode, request.login_remember_me = (
                    self.decode_jwt(token))
            except Exception:
                request.user = AnonymousUser()
                request.delete_cookie = True
        else:
            if not hasattr(request, 'user'):
                request.user = AnonymousUser()

    def process_response(self, request, response):
        if getattr(request, 'delete_cookie', False):
            return delete_token_cookie(response)
        return response
