import json
from unittest.mock import MagicMock

from django.db import models
from django.test import TestCase

from pfx.pfxcore.exceptions import ModelValidationAPIError
from pfx.pfxcore.models import PFXModelMixin
from pfx.pfxcore.test import TestAssertMixin
from pfx.pfxcore.views import BodyMixin


class CustomModel(PFXModelMixin, models.Model):
    value = models.IntegerField("An integer")

    class Meta:
        managed = False


class CustomView(BodyMixin):
    def __init__(self, **body):
        super().__init__()
        self.request = MagicMock()
        self.request.body = json.dumps(body)


class TestBodyMixin(TestAssertMixin, TestCase):
    def test_body_to_model(self):
        view = CustomView(value=7)
        custom = view.body_to_model(CustomModel)

        self.assertIsInstance(custom, CustomModel)
        self.assertEqual(custom.value, 7)

    def test_body_to_model_ignore_auto_fields(self):
        view = CustomView(id=99999, value=7)
        custom = view.body_to_model(CustomModel)

        self.assertIsInstance(custom, CustomModel)
        self.assertNotEqual(custom.pk, 99999)
        self.assertEqual(custom.value, 7)

    def test_body_to_model_ignore_unknown_fields(self):
        view = CustomView(id=99999, value=7)
        custom = view.body_to_model(CustomModel)

        self.assertIsInstance(custom, CustomModel)
        self.assertNotEqual(custom.pk, 99999)
        self.assertEqual(custom.value, 7)

    def test_body_to_model_validation(self):
        view = CustomView()
        with self.assertRaises(ModelValidationAPIError) as cm:
            view.body_to_model(CustomModel)
        self.assertJE(
            cm.exception.data.message_dict, "value",
            ["This field cannot be null."])

    def test_body_to_model_disable_validation(self):
        view = CustomView()
        custom = view.body_to_model(CustomModel, validate=False)

        self.assertIsInstance(custom, CustomModel)
        self.assertEqual(custom.value, None)
