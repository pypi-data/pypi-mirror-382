from django.contrib.auth.models import (
    AbstractBaseUser,
    AbstractUser,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _

from .pfx_models import PFXModelMixin


class AbstractPFXBaseUser(PFXModelMixin, AbstractBaseUser):
    """The base abstract user for PFX."""

    class Meta:
        abstract = True

    def auth_json_repr(self, **kw):
        res = self.json_repr(
            username=self.get_username(),
            is_active=self.is_active,
            **kw)
        email_field = self.get_email_field_name()
        if email_field != self.USERNAME_FIELD and hasattr(self, email_field):
            res['email'] = getattr(self, email_field)
        if isinstance(self, PermissionsMixin):
            res['is_superuser'] = self.is_superuser
            res['permissions'] = list(self.get_all_permissions())
        return res

    @classmethod
    def auth_json_repr_schema(cls):
        return cls.json_repr_schema()

    def get_user_jwt_signature_key(self):
        """
        Return a user secret to sign JWT token.

        If not empty, the JWT token validity depends on all values
        user to build the return string. So, each time the returned value
        changes, the previously issued tokens will no longer be valid.
        """
        return self.password

    def on_user_set_password(self, first_time=False):
        pass


class AbstractPFXUser(AbstractUser, AbstractPFXBaseUser):
    """The base abstract user for PFX with permissions mixin."""

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        abstract = True

    def auth_json_repr(self, **kw):
        res = super().auth_json_repr(
            first_name=self.first_name,
            last_name=self.last_name,
            is_staff=self.is_staff,
            date_joined=self.date_joined,
            last_login=self.last_login,
            **kw)
        return res
