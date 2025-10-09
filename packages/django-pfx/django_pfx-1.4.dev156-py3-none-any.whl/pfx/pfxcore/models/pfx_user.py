# from django.contrib.auth.models import AbstractUser

from .abstract_pfx_base_user import AbstractPFXUser


class PFXUser(AbstractPFXUser):
    """The Django User with PFX mixins.
    """

    class Meta(AbstractPFXUser.Meta):
        swappable = "AUTH_USER_MODEL"
