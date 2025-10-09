from datetime import date

from django.db import connection, models
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import include, path

from pfx.pfxcore import register_views
from pfx.pfxcore.decorator import rest_view
from pfx.pfxcore.models import JSONReprMixin
from pfx.pfxcore.test import APIClient, TestAssertMixin
from pfx.pfxcore.views import RestView
from tests.views import FakeViewMixin


class TestDateModel(JSONReprMixin, models.Model):
    date_at = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "TestModel"
        verbose_name_plural = "TestModels"
        ordering = ['pk']


@rest_view("/test")
class TestDateRestView(FakeViewMixin, RestView):
    default_public = True
    model = TestDateModel


urlpatterns = [
    path('api/', include(register_views(TestDateRestView))),
    path('api/', include('pfx.pfxcore.urls'))
]


@override_settings(ROOT_URLCONF=__name__)
class TestFieldsDate(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')

    @classmethod
    def setUpTestData(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TestDateModel)

    def test_update_null(self):
        c1 = TestDateModel.objects.create(date_at=date(2025, 5, 3))

        response = self.client.put(f'/api/test/{c1.pk}', dict(date_at=None))
        self.assertRC(response, 200)
        self.assertJE(response, 'date_at', None)

    def test_update_empty_string(self):
        c1 = TestDateModel.objects.create(date_at=date(2025, 5, 3))

        response = self.client.put(f'/api/test/{c1.pk}', dict(date_at=""))
        self.assertRC(response, 200)
        self.assertJE(response, 'date_at', None)
