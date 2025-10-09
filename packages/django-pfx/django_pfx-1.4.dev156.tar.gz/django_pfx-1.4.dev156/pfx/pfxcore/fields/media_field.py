import logging
from importlib import import_module
from urllib.request import urlopen

from django.db import models
from django.db.models.signals import post_delete, post_init
from django.dispatch import receiver

from pfx.pfxcore.shortcuts import settings

logger = logging.getLogger(__name__)


def get_storage_class(class_path):
    ps = class_path.split('.')
    return getattr(import_module('.'.join(ps[:-1])), ps[-1])()


class MediaField(models.JSONField):
    def __init__(
            self, *args, max_length=255, get_key=None, storage=None,
            auto_delete=False, **kwargs):
        self.get_key = get_key or self.get_default_key
        if not storage and not settings.STORAGE_DEFAULT:
            raise Exception(
                "Missing storage. You have to set a storage "
                "class on the field or define STORAGE_DEFAULT settings.")
        self.storage = storage or get_storage_class(settings.STORAGE_DEFAULT)
        self.auto_delete = auto_delete
        self._db_value = None
        super().__init__(
            *args, max_length=max_length, **kwargs)

    @staticmethod
    def get_default_key(obj, filename):
        return f"{type(obj).__name__}/{obj.pk}/{filename}"

    def media_pre_save(self, obj):
        def save_file(obj, file, name):
            setattr(obj, self.name, self.upload(obj, file, name))
            obj.save(update_fields={self.name})

        after_save = []
        value = self.value_from_object(obj)
        if isinstance(value, dict):
            b64 = value.pop('base64', None)
            name = value.get('name')
        else:
            b64 = None

        if self._db_value and (b64 or not value):
            after_save.append(lambda: self.delete(self._db_value))
            setattr(obj, self.name, None)
        if b64:
            with urlopen(b64) as response:
                file = response.read()
            setattr(obj, self.name, dict(key=self.get_key(obj, file)))
            after_save.append(lambda: save_file(obj, file, name))
        return after_save

    def to_python(self, value):
        return super().to_python(self.storage.to_python(value))

    def get_upload_url(self, request, obj, filename):
        key = self.get_key(obj, filename)
        url = self.storage.get_upload_url(request, key)
        return dict(url=url, file=dict(name=filename, key=key))

    def get_url(self, request, obj):
        return self.storage.get_url(
            request, self.value_from_object(obj)['key'])

    def upload(self, obj, file, filename, **kwargs):
        key = self.get_key(obj, filename)
        return self.to_python(self.storage.upload(key, file, **kwargs))

    def delete(self, value):
        return self.storage.delete(value)


@receiver(post_init)
def post_init_media(sender, instance, **kwargs):
    for field in sender._meta.fields:
        if isinstance(field, MediaField):
            field._db_value = field.value_from_object(instance)


@receiver(post_delete)
def post_delete_media(sender, instance, **kwargs):
    for field in sender._meta.fields:
        if isinstance(field, MediaField) and field.auto_delete:
            field.storage.delete(field.value_from_object(instance))
