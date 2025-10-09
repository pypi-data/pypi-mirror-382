from django.db import connection, models
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import include, path
from django.utils.translation import gettext_lazy as _

from pfx.pfxcore import register_views
from pfx.pfxcore.decorator import rest_view
from pfx.pfxcore.models import JSONReprMixin
from pfx.pfxcore.test import APIClient, TestAssertMixin
from pfx.pfxcore.views import RestView
from tests.views import FakeViewMixin

# Add i18n string for Value 2, to check this is not used to translate
# the same value in choices.
_("Value 2")


class TestChoicesModel(JSONReprMixin, models.Model):
    choice1 = models.CharField(max_length=30, choices=[
        ('v1', "Value 1"),
        ('v2', "Value 2"),
    ])
    choice2 = models.CharField(max_length=30, choices=[
        ('v3', _("Value 3")),
        ('v4', _("Value 4")),
    ])

    class Meta:
        verbose_name = "TestModel"
        verbose_name_plural = "TestModels"
        ordering = ['pk']


@rest_view("/test")
class TestChoicesRestView(FakeViewMixin, RestView):
    default_public = True
    model = TestChoicesModel


urlpatterns = [
    path('api/', include(register_views(TestChoicesRestView))),
    path('api/', include('pfx.pfxcore.urls'))
]


@override_settings(ROOT_URLCONF=__name__)
class TestFieldsChoices(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')

    @classmethod
    def setUpTestData(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TestChoicesModel)

    def test_meta(self):
        response = self.client.get('/api/test/meta', locale='fr')
        self.assertRC(response, 200)
        self.assertJE(response, 'fields.choice1.choices.@0.label', "Value 1")
        self.assertJE(response, 'fields.choice1.choices.@1.label', "Value 2")
        self.assertJE(response, 'fields.choice2.choices.@0.label', "Valeur 3")
        self.assertJE(response, 'fields.choice2.choices.@1.label', "Valeur 4")

    def test_meta_list(self):
        response = self.client.get('/api/test/meta/list', locale='fr')
        self.assertRC(response, 200)
        self.assertJE(response, 'fields.choice1.choices.@0.label', "Value 1")
        self.assertJE(response, 'fields.choice1.choices.@1.label', "Value 2")
        self.assertJE(response, 'fields.choice2.choices.@0.label', "Valeur 3")
        self.assertJE(response, 'fields.choice2.choices.@1.label', "Valeur 4")

    def test_get(self):
        c1 = TestChoicesModel.objects.create(choice1='v2', choice2='v3')

        response = self.client.get(f'/api/test/{c1.pk}', locale='fr')
        self.assertRC(response, 200)
        self.assertJE(response, 'choice1.label', "Value 2")
        self.assertJE(response, 'choice2.label', "Valeur 3")

    def test_get_list(self):
        TestChoicesModel.objects.create(choice1='v2', choice2='v3')

        response = self.client.get('/api/test', locale='fr')
        self.assertRC(response, 200)
        self.assertJE(response, 'items.@0.choice1.label', "Value 2")
        self.assertJE(response, 'items.@0.choice2.label', "Valeur 3")
