from pfx.pfxcore import PfxAppConfig


class AccountConfig(PfxAppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tests'
    default = True
