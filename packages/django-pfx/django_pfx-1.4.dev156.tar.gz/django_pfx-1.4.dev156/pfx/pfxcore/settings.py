from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from . import default_settings


class PFXSettings:
    def __getattr__(self, name):
        try:
            val = getattr(django_settings, name)
        except AttributeError:
            if hasattr(default_settings, name):
                val = getattr(default_settings, name)
            else:
                raise
        if name == "PFX_SECRET_KEY" and not val:
            raise ImproperlyConfigured(
                "The PFX_SECRET_KEY setting must not be empty.")
        return val


settings = PFXSettings()
