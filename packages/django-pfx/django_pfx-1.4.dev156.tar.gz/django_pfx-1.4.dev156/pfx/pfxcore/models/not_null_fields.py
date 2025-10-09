from django.db import models


class NotNullFieldMixin:
    def __init__(self, *args, **kwargs):
        kwargs['null'] = False
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        return "" if value is None else value


class NotNullCharField(NotNullFieldMixin, models.CharField):
    pass


class NotNullTextField(NotNullFieldMixin, models.TextField):
    pass


class NotNullURLField(NotNullFieldMixin, models.URLField):
    pass
