from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from pfx.pfxcore.decorator import rest_property
from pfx.pfxcore.settings import settings


class OtpUserMixin(models.Model):
    """A mixin to enable OTP MFA on a user class."""

    #: OTP secret token.
    otp_secret_token = models.CharField(
        _("OTP secret token"), max_length=32, null=True,
        blank=True, unique=True)
    #: Temporary OTP secret token (needs confirmation).
    otp_secret_token_tmp = models.CharField(
        _("Temporary OTP secret token"), max_length=32, null=True, blank=True)
    #: HOTP count.
    hotp_count = models.IntegerField(_("HOTP count"), default=0)
    #: HOTP expiry.
    hotp_expiry = models.DateTimeField(_("HOTP expiry"), default=timezone.now)

    class Meta:
        abstract = True

    @rest_property(_("OTP enabled"), "BooleanField")
    def is_otp(self):
        return bool(self.otp_secret_token)

    def enable_otp(self):
        """Activate OTP for this user.

        Generates a new temporary OTP secret token. To complete activation,
        call `confirm_otp` with a valid code.
        """
        import pyotp
        self.otp_secret_token_tmp = pyotp.random_base32()
        self.save(update_fields=['otp_secret_token_tmp'])

    def confirm_otp(self, otp_code):
        """Confirm OTP activation for this user.

        Set the OTP secret token from the temporary one if the provided
        code is valid.

        :param otp_code: A valid OTP code for the temporary OTP secret key.
        :returns: `True` if success, `False` otherwise.
        """
        if self.is_otp_valid(otp_code, tmp=True):
            self.otp_secret_token = self.otp_secret_token_tmp
            self.otp_secret_token_tmp = None
            self.save(update_fields=[
                'otp_secret_token', 'otp_secret_token_tmp'])
            return True
        return False

    def disable_otp(self):
        """Disable OTP for this user.

        Remove the OTP secret token.
        """
        self.otp_secret_token = None
        self.save(update_fields=['otp_secret_token'])

    def get_otp_setup_uri(self, tmp=False, with_color=True):
        """Return the setup URL for OTP activation.
        """
        import pyotp
        args = dict(
            name=self.get_username(), issuer_name=settings.PFX_SITE_NAME)
        if settings.PFX_OTP_IMAGE:
            args['image'] = settings.PFX_OTP_IMAGE
        uri = pyotp.totp.TOTP(
            tmp and self.otp_secret_token_tmp or
            self.otp_secret_token).provisioning_uri(**args)
        if with_color and settings.PFX_OTP_COLOR:
            # TODO: Can be put in provisioning_uri args if
            # https://github.com/pyauth/pyotp/pull/164 is merge and published.
            uri = f"{uri}&color={settings.PFX_OTP_COLOR}"
        return uri

    def is_otp_valid(self, otp_code, tmp=False):
        """Verify an OTP code.

        :param otp_code: A valid OTP code for the OTP secret key.
        :param tmp: If `True`, verify the code with the temporary
            OTP secret key.
        :returns: `True` if the code is valid, `False` otherwise.
        """
        import pyotp

        # TODO : The with_color paramter can be removed if
        # https://github.com/pyauth/pyotp/pull/164 is merge and published.
        totp = pyotp.parse_uri(
            self.get_otp_setup_uri(tmp=tmp, with_color=False))
        valid = totp.verify(
            otp_code, valid_window=settings.PFX_OTP_VALID_WINDOW)
        if not valid and timezone.now() <= self.hotp_expiry:
            hotp = pyotp.hotp.HOTP(
                tmp and self.otp_secret_token_tmp or
                self.otp_secret_token)
            return hotp.verify(otp_code, self.hotp_count)
        return valid

    def get_user_jwt_signature_key(self):
        """Return a user secret to sign JWT token.

        If the user inherit :class:`pfx.pfxcore.models.AbstractPFXBaseUser`,
        add the OTP secret token to the user signature."""
        return super().get_user_jwt_signature_key() + (
            self.otp_secret_token or "")

    def get_hotp_code(self):
        """Return a new valid HOTP code.

        Increment the HOTP counter and reset the expiry."""
        import pyotp
        if not self.otp_secret_token:
            raise Exception("OTP disabled")
        self.hotp_count += 1
        self.hotp_expiry = timezone.now() + timedelta(
            minutes=settings.PFX_HOTP_CODE_VALIDITY)
        self.save(update_fields=[
            'hotp_count', 'hotp_expiry'])
        return pyotp.hotp.HOTP(self.otp_secret_token).at(self.hotp_count)
