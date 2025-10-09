from decimal import Decimal

from django.db import connection, models
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import include, path

from pfx.pfxcore import register_views
from pfx.pfxcore.decorator import rest_property, rest_view
from pfx.pfxcore.fields import DecimalField
from pfx.pfxcore.models import JSONReprMixin
from pfx.pfxcore.test import APIClient, TestAssertMixin
from pfx.pfxcore.views import RestView
from tests.views import FakeViewMixin


class TestDecimalModel(JSONReprMixin, models.Model):
    decimal = DecimalField(
        max_digits=10, decimal_places=5, json_decimal_places=2)
    percent = DecimalField(
        max_digits=10, decimal_places=4, percent=True)
    monetary = DecimalField(
        max_digits=10, decimal_places=5, json_decimal_places=2,
        currency="CHF")

    @rest_property(field=DecimalField(
        max_digits=10, decimal_places=5, json_decimal_places=2,
        currency="CHF"))
    def price_double(self):
        return Decimal(self.monetary * 2)

    class Meta:
        verbose_name = "TestModel"
        verbose_name_plural = "TestModels"
        ordering = ['pk']


@rest_view("/test-decimal-model")
class DecimalModelRestView(FakeViewMixin, RestView):
    default_public = True
    model = TestDecimalModel
    fields = ['decimal', 'percent', 'monetary', 'price_double']


urlpatterns = [
    path('api/', include(register_views(DecimalModelRestView))),
    path('api/', include('pfx.pfxcore.urls'))
]


@override_settings(ROOT_URLCONF=__name__)
class TestFieldsDecimal(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')

    @classmethod
    def setUpTestData(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TestDecimalModel)

    def test_decimal_meta(self):
        response = self.client.get('/api/test-decimal-model/meta')
        self.assertRC(response, 200)
        self.assertJE(response, 'fields.decimal.percent', False)
        self.assertJE(response, 'fields.decimal.currency', None)
        self.assertJE(response, 'fields.percent.percent', True)
        self.assertJE(response, 'fields.percent.currency', None)
        self.assertJE(response, 'fields.monetary.percent', False)
        self.assertJE(response, 'fields.monetary.currency', "CHF")
        self.assertJE(response, 'fields.price_double.percent', False)
        self.assertJE(response, 'fields.price_double.currency', "CHF")

    def test_decimal(self):
        t = TestDecimalModel.objects.create(
            decimal=3.14, percent=0.0810, monetary=100)
        t.save()
        t.refresh_from_db()
        self.assertEqual(t.decimal, Decimal('3.14000'))
        self.assertEqual(t.percent, Decimal('0.0810'))

        response = self.client.get(f'/api/test-decimal-model/{t.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'decimal', "3.14")
        self.assertJE(response, 'percent', "8.10")
        self.assertJE(response, 'monetary', "100.00")
        self.assertJE(response, 'price_double', "200.00")

        response = self.client.put(f'/api/test-decimal-model/{t.pk}', dict(
            decimal="3.12121",
            percent="7.7",
        ))
        self.assertRC(response, 200)
        self.assertJE(response, 'decimal', "3.12")
        self.assertJE(response, 'percent', "7.70")

        t.refresh_from_db()
        self.assertEqual(t.decimal, Decimal('3.12121'))
        self.assertEqual(t.percent, Decimal('0.0770'))
