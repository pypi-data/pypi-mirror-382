import logging
from datetime import datetime, timedelta, timezone

from django.contrib.auth import (
    authenticate,
    get_user_model,
    password_validation,
)
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.db import transaction
from django.template import loader
from django.utils import timezone as tz
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters

import jwt

from pfx.pfxcore.apidoc import Schema, Tag
from pfx.pfxcore.decorator import rest_api, rest_doc, rest_view
from pfx.pfxcore.exceptions import (
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from pfx.pfxcore.http import JsonResponse
from pfx.pfxcore.middleware.authentication import JWTTokenDecodeMixin
from pfx.pfxcore.models import CacheableMixin, OtpUserMixin
from pfx.pfxcore.models.login_ban import LoginBan
from pfx.pfxcore.settings import settings
from pfx.pfxcore.shortcuts import delete_token_cookie

from .rest_views import (
    BaseRestView,
    BodyMixin,
    CreateRestViewMixin,
    ModelMixin,
)

logger = logging.getLogger(__name__)
UserModel = get_user_model()
AUTHENTICATION_TAG = Tag("Authentication")


def token_validity(preset):
    presets = dict(
        short=settings.PFX_TOKEN_SHORT_VALIDITY,
        long=settings.PFX_TOKEN_LONG_VALIDITY,
        otp=settings.PFX_TOKEN_OTP_VALIDITY)
    return timedelta(**presets[preset])


@rest_view("/auth")
class AuthenticationView(
        ModelMixin, BodyMixin, JWTTokenDecodeMixin, BaseRestView):
    """The authentication view."""

    model = UserModel
    tags = [AUTHENTICATION_TAG]
    #: The token generator.
    token_generator = default_token_generator

    def login_failed_response(self):
        """Return the response for login failed.

        Can be overridden to customize the error."""
        raise AuthenticationError()

    def login_ban_response(self, ban_dt):
        """Return the response for login temporary ban.

        Can be overridden to customize the error."""
        seconds = int(ban_dt.total_seconds())
        response = JsonResponse(dict(
            message=_(
                "Your connection is temporarily disabled after several "
                "unsuccessful attempts, please retry in {seconds} seconds."
            ).format(seconds=seconds)), status=429)
        response['Retry-after'] = seconds
        return response

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    @rest_api(
        "/login", public=True, method="post", priority_doc=0,
        response_schema='login_schema')
    def login(self, *args, **kwargs):
        """Entrypoint for :code:`POST /login` route.

        Use the request body to authenticate the user using
        the username and password attributes.

        :returns: The JSON response
        :rtype: :class:`JsonResponse`
        ---
        post:
            summary: Login
            description: A login rest services with a `mode` parameter to
                choose between JWT bearer token or cookie authentication.
                In cookie mode, the JWT token is saved in an HTTP-only cookie.
            requestBody:
                content:
                    application/json:
                        schema:
                            properties:
                                username:
                                    type: string
                                password:
                                    type: string
                                    format: password
                                remember_me:
                                    description: If true, use a long validity
                                        token to keep the user logged in
                                        for a long time.
                                    type: boolean
            parameters:
              - in: query
                name: mode
                schema:
                    type: string
                    enum: ['jwt', 'cookie']
                    default: 'jwt'
            responses:
                422:
                    description: The credentials are not valid.
                429:
                    description: Temporary banned after several unsuccessful
                        attempts.
        """
        data = self.deserialize_body()
        username = data.get('username')
        ban_dt = LoginBan.objects.is_ban(username)
        if ban_dt:
            return self.login_ban_response(ban_dt)
        user = authenticate(self.request, username=username,
                            password=data.get('password'))
        if isinstance(user, CacheableMixin):
            user.cache_delete()
        if user is None:
            LoginBan.objects.ban(username)
            return self.login_failed_response()
        LoginBan.objects.unban(username)
        mode = self.request.GET.get('mode', 'jwt')
        remember_me = data.get('remember_me', False)
        if isinstance(user, OtpUserMixin) and user.otp_secret_token:
            return self._login_need_otp_response(user, mode, remember_me)
        return self._login_success(user, mode, remember_me)

    def _login_success(
            self, user, mode, remember_me=False, message=None):
        user.last_login = tz.now()
        user.save(update_fields=['last_login'])
        token = self._prepare_token(user, mode, remember_me)
        if mode == 'cookie':
            if remember_me:
                expires = datetime.now(
                    tz=timezone.utc) + token_validity('long')
            else:
                expires = None  # create a session cookie

            res = JsonResponse(dict(
                need_otp=False,
                user=self.get_user_information(user)))
            res.set_cookie(
                'token', token, secure=settings.PFX_COOKIE_SECURE,
                expires=expires, domain=settings.PFX_COOKIE_DOMAIN,
                httponly=True, samesite=settings.PFX_COOKIE_SAMESITE)
            return res
        return JsonResponse(dict(
            message=message or _("Successful login"),
            need_otp=False,
            token=token,
            user=self.get_user_information(user)))

    def _login_need_otp_response(self, user, mode, remember_me=False):
        """Return the response for login if OTP login is needed.

        Can be overridden to customize the response."""
        token = self._prepare_token(user, mode, remember_me, otp_login=True)
        return JsonResponse(dict(need_otp=True, token=token))

    @method_decorator(never_cache)
    @rest_api(
        "/logout", public=True, method="get", priority_doc=1,
        response_schema='message_schema')
    def logout(self, *args, **kwargs):
        """Entrypoint for :code:`GET /logout` route.

        :returns: The JSON response
        :rtype: :class:`JsonResponse`
        ---
        get:
            summary: Logout
            description: A service that deletes the authentication cookie
                if it exists.
        """
        return delete_token_cookie(JsonResponse(dict(message="Goodbye")))

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    @rest_api(
        "/change-password", method="post", priority_doc=2,
        response_schema='message_schema')
    def change_password(self, *args, **kwargs):
        """Entrypoint for :code:`POST /change-password` route.

        :returns: The JSON response
        :rtype: :class:`JsonResponse`
        ---
        post:
            summary: Change password
            description: A service to change the password of
                an authenticated user.
            requestBody:
                content:
                    application/json:
                        schema:
                            properties:
                                old_password:
                                    description: the user's current password
                                    type: string
                                    format: password
                                new_password:
                                    description: the user's future password
                                    type: string
                                    format: password
        """
        data = self.deserialize_body()
        user = authenticate(self.request,
                            username=self.request.user.get_username(),
                            password=data.get('old_password'))
        errors = dict()
        try:
            if user is not None and data.get('new_password'):
                password_validation.validate_password(data['new_password'],
                                                      user)
                user.set_password(data.get('new_password'))
                user.save()

                user.on_user_set_password(first_time=False)

                return JsonResponse({
                    'message': _('password updated successfully')
                })
        except ValidationError as e:
            errors['new_password'] = e.error_list
        if not user:
            errors['old_password'] = [_("Incorrect password")]
        if not data.get('new_password'):
            errors.setdefault('new_password', []).append(
                _("Empty password is not allowed"))
        return JsonResponse(
            ValidationError(errors), status=422)

    def _prepare_token(
            self, user, mode='jwt', remember_me=False, otp_login=False,
            **extra_payload):
        exp = datetime.now(tz=timezone.utc) + token_validity(
            otp_login and 'otp' or (remember_me and 'long' or 'short'))
        payload = dict(
            exp=exp,
            pfx_login_options=[mode, remember_me],
            pfx_otp_login=otp_login,
            **self.get_extra_payload(user), **extra_payload)
        return jwt.encode(
            payload,
            user.get_user_jwt_signature_key() + settings.PFX_SECRET_KEY,
            headers=dict(pfx_user_pk=user.pk),
            algorithm="HS256")

    def get_extra_payload(self, user):
        """Get extra payload for user token.

        By default, there is only one private claim in the JWT token
        (exp : expiration). This method can be overridden
        to add claims (key: value attributes) to the JWT token.

        :param user: The user
        :returns: The extra payload
        :rtype: :class:`dict`"""
        return {}

    def get_user_information(self, user):
        """Get the user representation in the view.

        Can be overridden to customize result.

        :param user: The user"""
        info = user.auth_json_repr()
        if isinstance(user, OtpUserMixin):
            info.update(is_otp=user.is_otp)
        return info

    @classmethod
    def get_user_information_schema(cls):
        """Get user representation schema.

        Can be overridden to customize result."""
        return Schema(
            'auth_user', "User", **UserModel.auth_json_repr_schema())

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    @rest_api(
        "/validate-user-token", public=True, method="post", priority_doc=4,
        response_schema='message_schema')
    def validate_user_token(self, *args, **kwargs):
        """Entrypoint for :code:`POST /validate-user-token` route.

        Validate the uid and the set/reset password token contained
        in self.request.body.

        :returns: The JSON response
        :rtype: :class:`JsonResponse`
        ---
        post:
            summary: Validate user token
            description:  Validate the uidb64 and
                the token sent in the set/reset password link.
            requestBody:
                content:
                    application/json:
                        schema:
                            properties:
                                uidb64:
                                    type: string
                                    description: the uid in base64 sent in
                                        the set/reset password link
                                token:
                                    type: string
                                    description: the reset password token
                                        sent in the set/reset password link
        """
        data = self.deserialize_body()
        assert 'uidb64' in data and 'token' in data

        user = self.get_user(data['uidb64'])

        if (user is not None and
                self.token_generator.check_token(user, data['token'])):
            return JsonResponse(
                ValidationError(_('User and token are valid')), status=200)
        return JsonResponse(
            ValidationError(_('User or token is invalid')), status=422)

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    @rest_api(
        "/set-password", public=True, method="post", priority_doc=3,
        response_schema='login_or_message_schema')
    def set_password(self, *args, **kwargs):
        """Entrypoint for :code:`POST /set-password` route.

        Set the password if the base64 uid and the set/reset password
        token are valid. Password, uid and set/reset password token are
        retrieved in self.request.body

        :returns: The JSON response
        :rtype: :class:`JsonResponse`
        ---
        post:
            summary: Set password
            description: A service for setting the password using a UID and
                a token provided in the email sent by the "forgotten password"
                 or "sign up" services.
            requestBody:
                content:
                    application/json:
                        schema:
                            properties:
                                uidb64:
                                    type: string
                                    description: the uid in base64 sent in
                                        the set/reset password link
                                token:
                                    type: string
                                    description: the reset password token sent
                                        in the set/reset password link
                                password:
                                    description: the new password
                                    type: string
                                    format: password
                                autologin:
                                    description: Automatically logs the user in
                                        upon successful authentication,
                                        utilizing the value of this property
                                        as the login mode.
                                    type: string
                                    enum: ['jwt', 'cookie']
        """
        data = self.deserialize_body()
        assert 'uidb64' in data and 'token' in data

        user = self.get_user(data['uidb64'])

        try:
            if (user is not None and data.get('password') and
                    self.token_generator.check_token(user, data['token'])):
                password_validation.validate_password(data['password'], user)
                user.set_password(data['password'])
                user.save()
                user.refresh_from_db()

                if not user.last_login:
                    user.on_user_set_password(first_time=True)
                else:
                    user.on_user_set_password(first_time=False)

                if 'autologin' in data and data['autologin'] in (
                        'jwt', 'cookie'):
                    return self._login_success(user, data['autologin'])
                return JsonResponse({
                    'message': _('password updated successfully')
                })
        except ValidationError as e:
            return JsonResponse(
                ValidationError(dict(password=e.error_list)), status=422)

        if not data.get('password'):
            return JsonResponse(
                ValidationError(dict(
                    password=_("Empty password is not allowed"))), status=422)
        raise UnauthorizedError()

    @method_decorator(never_cache)
    @rest_api("/otp/setup-uri", public=False, method="get", priority_doc=52)
    def otp_setup_uri(self, *args, **kwargs):
        """Entrypoint for :code:`GET /otp/secret-key` route.

        Get the setup uri for the OTP authentication.

        :returns: The JSON response
        :rtype: :class:`JsonResponse`
        ---
        put:
            summary: Get the activation url for the OTP authentication.
            description: This service returns a setup URI to enable the OTP.
                Your front-end application should provide this URI in the form
                of a QR code so that the user can scan it with
                an OTP application. You must then call the /confirm service
                with a valid OTP code to activate OTP authentication.
            responses:
                200:
                    content:
                        application/json:
                            schema:
                                properties:
                                    setup_uri:
                                        type: string
        """
        if not isinstance(self.request.user, OtpUserMixin):
            logger.error("User must inherit OtpUserMixin to activate OTP")
            raise NotFoundError()
        if self.request.user.otp_secret_token:
            return JsonResponse(
                dict(message=_("OTP is already enabled")), status=400)
        self.request.user.enable_otp()
        return JsonResponse(dict(
            setup_uri=self.request.user.get_otp_setup_uri(tmp=True)))

    @method_decorator(never_cache)
    @rest_api(
        "/otp/enable", public=False, method="put", priority_doc=53,
        response_schema='message_schema')
    def otp_enable(self, *args, **kwargs):
        """Entrypoint for :code:`PUT /otp/enable` route.

        Enable the OTP authentication.

        :returns: The JSON response
        :rtype: :class:`JsonResponse`
        ---
        put:
            summary: Enable OTP authentication
            description: A service to enable the OTP authentication with a
                valid OTP code.
            requestBody:
                content:
                    application/json:
                        schema:
                            properties:
                                otp_code:
                                    type: string
                                    description: a valid OTP code
            responses:
                422:
                    description: If the OTP code is not valid.
        """
        if not isinstance(self.request.user, OtpUserMixin):
            logger.error("User must inherit OtpUserMixin to activate OTP")
            raise NotFoundError()
        data = self.deserialize_body()
        if self.request.user.confirm_otp(data.get('otp_code')):
            return self._login_success(
                self.request.user, self.request.login_mode,
                self.request.login_remember_me, message=_("OTP enabled"))
        return JsonResponse(dict(otp_code=[_("Invalid code")]), status=422)

    @method_decorator(never_cache)
    @rest_api("/otp/disable", public=False, method="put", priority_doc=54)
    def otp_disable(self, *args, **kwargs):
        """Entrypoint for :code:`PUT /otp/disable` route.

        Disable the OTP authentication.

        :returns: The JSON response
        :rtype: :class:`JsonResponse`
        ---
        put:
            summary: Disable OTP
            description: A service to disable the OTP authentication.
            requestBody:
                content:
                    application/json:
                        schema:
                            properties:
                                otp_code:
                                    type: string
                                    description: a valid OTP code
            responses:
                422:
                    description: If the OTP code is not valid.
        """
        if not isinstance(self.request.user, OtpUserMixin):
            logger.error("User must inherit OtpUserMixin to activate OTP")
            raise NotFoundError()
        data = self.deserialize_body()
        if self.request.user.is_otp_valid(data.get('otp_code')):
            self.request.user.disable_otp()
            return self._login_success(
                self.request.user, self.request.login_mode,
                self.request.login_remember_me, message=_("OTP disabled"))
        return JsonResponse(dict(otp_code=[_("Invalid code")]), status=422)

    @method_decorator(never_cache)
    @rest_api(
        "/otp/login", public=True, method="post", priority_doc=50,
        response_schema='login_schema')
    def otp_login(self, *args, **kwargs):
        """Entrypoint for :code:`PUT /otp/login` route.

        Login a user with a valid OTP code.

        :returns: The JSON response
        :rtype: :class:`JsonResponse`
        ---
        post:
            summary: OTP login
            description: A login service which validate the OTP code.
            requestBody:
                content:
                    application/json:
                        schema:
                            properties:
                                token:
                                    type: string
                                    description: a valid JWT user token
                                otp_code:
                                    type: string
                                    description: a valid OTP code
            responses:
                422:
                    description: If OTP code is missing, invalid or expired.
                429:
                    description: Temporary banned after several unsuccessful
                        attempts.
                401:
                    description: If the token is missing, invalid or expired.
                403:
                    description: If the OTP is disabled for this user.
        """
        data = self.deserialize_body()
        token = data.get('token', "")
        try:
            user_pk = self.decode_jwt_header(token)
            ban_key = f"otp_{user_pk}"
        except Exception:
            raise UnauthorizedError()
        ban_dt = LoginBan.objects.is_ban(ban_key)
        if ban_dt:
            return self.login_ban_response(ban_dt)
        try:
            user, mode, remember_me = self.decode_jwt(token, otp_login=True)
        except Exception:
            raise UnauthorizedError()
        if not isinstance(user, OtpUserMixin):
            logger.error("User must inherit OtpUserMixin to activate OTP")
            raise NotFoundError()
        if not user.otp_secret_token:
            raise ForbiddenError()
        if user.is_otp_valid(data.get('otp_code')):
            LoginBan.objects.unban(ban_key)
            return self._login_success(user, mode, remember_me)
        LoginBan.objects.ban(ban_key)
        return self.login_failed_response()

    def get_user(self, uidb64):
        """Get user by token

        :param uidb64: The token"""
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist,
                ValidationError):
            user = None
        return user

    @classmethod
    def generate_schemas(cls):
        """Generate schemas for the class.
        """
        super().generate_schemas()
        cls.login_schema = Schema("login", "Login", properties=dict(
            need_otp=dict(
                type='boolean',
                description="`true` if an OTP login is required "
                "for this user"),
            token=dict(
                type='string',
                description="Returned if `mode` is `'jwt'` or if `need_otp` "
                "is `true` (in this case the token received is only valid "
                "for the OTP login service)"),
            user=dict(
                description="Returned only if `need_otp` is `false`",
                **cls.get_user_information_schema().to_schema())))
        cls.login_or_message_schema = Schema(
            "login_or_message",
            "Login or message (depending autologin parameter)",
            oneOf=[cls.message_schema.id(), cls.login_schema.id()])

    @classmethod
    def get_apidoc_schemas(cls):
        """Get schemas for the class.

        :returns: The schemas list
        :rtype: :class:`list[pfx.pfxcore.apidoc.Schema]`
        """
        return super().get_apidoc_schemas() + [
            cls.login_schema, cls.login_or_message_schema]


class SendMessageTokenMixin:
    """A mixin to send emails with user token."""

    #: The email template.
    email_template_name = None
    #: The email subject template.
    subject_template_name = None
    #: The token generator.
    token_generator = default_token_generator
    #: Extra email context.
    extra_email_context = None
    #: The from value of the email.
    from_email = None
    #: The HTML email template.
    html_email_template_name = None
    #: The email field of user model.
    email_field = 'email'
    #: The language field of user model
    language_field = 'language'

    def send_token_message(self, user):
        """Send an email to a user with a password reset link.

        :param user: The user
        """
        from django.utils import translation
        lang = str(getattr(user, self.language_field, settings.LANGUAGE_CODE))

        token = self.token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        data = {
            'target_user': user,
            'token': token,
            'uidb64': uidb64,
            'reset_url': self.reset_url(token, uidb64),
            'site_name': settings.PFX_SITE_NAME,
            'user': user,
            **(self.extra_email_context or {})
        }
        with translation.override(lang):
            subject = loader.render_to_string(self.subject_template_name, data)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            body = loader.render_to_string(self.email_template_name, data)
            email_message = EmailMultiAlternatives(
                subject, body, self.from_email,
                [getattr(user, self.email_field)])
            if self.html_email_template_name is not None:
                html_email = loader.render_to_string(
                    self.html_email_template_name, data)
                email_message.attach_alternative(
                    html_email, 'text/html')
            email_message.send()

    def reset_url(self, token, uidb64):
        """Get the password reset URL.

        :param token: The token
        :param uidb64: The user PK in base 64
        """
        return settings.PFX_RESET_PASSWORD_URL.format(
            token=token,
            uidb64=uidb64,
        )


@rest_doc("", "post", summary="Signup",
          description="A service that allows visitors to sign up.")
@rest_doc("/meta", "get", summary="Get signup metadata")
@rest_view("/auth/signup")
class SignupView(SendMessageTokenMixin, CreateRestViewMixin, BaseRestView):
    """The view for signup."""
    email_template_name = 'registration/welcome_email.txt'
    subject_template_name = 'registration/welcome_subject.txt'
    token_generator = default_token_generator
    extra_email_context = None
    from_email = None
    html_email_template_name = None
    default_public = True
    model = UserModel
    fields = ['first_name', 'last_name', 'username', 'email']
    tags = [AUTHENTICATION_TAG]

    def validate(self, obj, **kwargs):
        obj.set_unusable_password()
        super().validate(obj, **kwargs)

    def is_valid(self, obj, created=True, **kwargs):
        with transaction.atomic():
            r = super().is_valid(obj, created, **kwargs)
            self.send_token_message(obj)
        return r


@rest_view("/auth")
class ForgottenPasswordView(SendMessageTokenMixin, BodyMixin, BaseRestView):
    """View for forgotten password service."""
    email_template_name = 'registration/password_reset_email.txt'
    subject_template_name = 'registration/password_reset_subject.txt'
    token_generator = default_token_generator
    extra_email_context = None
    from_email = None
    html_email_template_name = None
    #: The ApiDoc tags.
    tags = [AUTHENTICATION_TAG]

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    @rest_api(
        "/forgotten-password", public=True, method="post",
        response_schema='message_schema')
    def forgotten_password(self, *args, **kwargs):
        """Entrypoint for :code:`POST /forgotten-password` route.

        Request a link to reset the password.
        Send an e-mail to the provided email address in the post body
        if it exits with a link to change the user password.

        :returns: The JSON response
        :rtype: :class:`JsonResponse`
        ---
        post:
            summary: Forgotten password
            description: Request an e-mail with a link
                to change the user password.
            requestBody:
                content:
                    application/json:
                        schema:
                            properties:
                                email:
                                    description: the user's email address
                                    type: string
        """
        data = self.deserialize_body()
        email = data.get('email')
        try:
            validate_email(email)
        except ValidationError as e:
            return JsonResponse(
                ValidationError(dict(email=e.error_list)), status=422)
        if email:
            try:
                user = UserModel._default_manager.get(email=email)
            except UserModel.DoesNotExist:
                user = None
            if user is not None:
                self.send_token_message(user)
        return JsonResponse({
            'message': _('If the email address you entered is correct, '
                         'you will receive an email from us with '
                         'instructions to reset your password.')
        })


@rest_view("/auth/otp")
class OtpEmailView(BodyMixin, JWTTokenDecodeMixin, BaseRestView):
    """View for the OTP code email service."""
    #: The email template.
    email_template_name = 'registration/otp_code_email.txt'
    #: The email subject template.
    subject_template_name = 'registration/otp_code_subject.txt'
    #: The HTML email template.
    html_email_template_name = None
    #: Extra email context.
    extra_email_context = None
    #: The from value of the email.
    from_email = None
    #: The email field of user model.
    email_field = 'email'
    #: The language field of user model
    language_field = 'language'
    #: The ApiDoc tags.
    tags = [AUTHENTICATION_TAG]

    @method_decorator(never_cache)
    @rest_api(
        "/email", public=True, method="post", priority_doc=51,
        response_schema='message_schema')
    def sent_email(self, *args, **kwargs):
        """Entrypoint for :code:`POST /email` route.

        Request a new OTP code by email.

        :returns: The JSON response
        :rtype: :class:`JsonResponse`
        ---
        post:
            summary: Send OTP email
            description: Request a new OTP code by email.
            requestBody:
                content:
                    application/json:
                        schema:
                            properties:
                                token:
                                    type: string
                                    description: a valid JWT user token. This
                                        is required only if the user is not
                                        already connected (with a Bearer token
                                        or a Cookie).
            responses:
                401:
                    description: If the token is missing, invalid or expired.
                403:
                    description: If the OTP is disabled for this user.
        """
        if self.request.user.is_anonymous:
            data = self.deserialize_body()
            try:
                user, __, __ = self.decode_jwt(
                    data.get('token', ""), otp_login=True)
            except Exception:
                raise UnauthorizedError()
        else:
            user = self.request.user
        if not isinstance(user, OtpUserMixin):
            logger.error("User must inherit OtpUserMixin to activate OTP")
            raise NotFoundError()
        if not user.otp_secret_token:
            raise ForbiddenError()
        self.send_otp_message(user)
        return JsonResponse({
            'message': _('A new authentication code has been sent by email.')})

    def send_otp_message(self, user):
        """Send an email to a user with an OTP code to a user.

        :param user: The user
        """
        from django.utils import translation
        lang = str(getattr(user, self.language_field, settings.LANGUAGE_CODE))

        otp_code = user.get_hotp_code()
        data = {
            'target_user': user,
            'otp_code': otp_code,
            'otp_validity': settings.PFX_HOTP_CODE_VALIDITY,
            'site_name': settings.PFX_SITE_NAME,
            'user': user,
            **(self.extra_email_context or {})
        }
        with translation.override(lang):
            subject = loader.render_to_string(self.subject_template_name, data)
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            body = loader.render_to_string(self.email_template_name, data)
            email_message = EmailMultiAlternatives(
                subject, body, self.from_email,
                [getattr(user, self.email_field)])
            if self.html_email_template_name is not None:
                html_email = loader.render_to_string(
                    self.html_email_template_name, data)
                email_message.attach_alternative(
                    html_email, 'text/html')
            email_message.send()
