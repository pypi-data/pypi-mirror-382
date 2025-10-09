from django.db import connection, models
from django.test import TestCase
from django.test.utils import override_settings

from pfx.pfxcore.fields import RichTextField
from pfx.pfxcore.models import JSONReprMixin
from pfx.pfxcore.test import TestAssertMixin


class TestRichTextFieldModel(JSONReprMixin, models.Model):
    html = RichTextField()
    custom_html = RichTextField(nh3_config='custom')

    class Meta:
        verbose_name = "TestModel"
        verbose_name_plural = "TestModels"
        ordering = ['pk']


@override_settings(ROOT_URLCONF=__name__)
class TestFieldsRichText(TestAssertMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TestRichTextFieldModel)

    def test_save(self):
        t = TestRichTextFieldModel.objects.create(
            html="<unknown>AAA</unknown>",
            custom_html='<h1>TEST</h1>'
            '<script>alert("hello")</script>'
            '<p><span class="test" style="font-family: noto;"></span></p>')
        self.assertEqual(t.html, "AAA")
        self.assertEqual(
            t.custom_html, '<h1>TEST</h1><p><span class="test"></span></p>')
