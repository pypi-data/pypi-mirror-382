from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import connection, models
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import include, path

from pfx.pfxcore import register_views
from pfx.pfxcore.decorator import rest_view
from pfx.pfxcore.models import JSONReprMixin
from pfx.pfxcore.test import APIClient, TestAssertMixin
from pfx.pfxcore.views import VF, RestView
from tests.views import FakeViewMixin


class TestOne2ManyModel(JSONReprMixin, models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        verbose_name = "TestOne2ManyModel"
        verbose_name_plural = "TestOne2ManyModel"
        ordering = ['pk']

    def clean_fields(self, exclude=None):
        errors = {}

        if 'rels' not in exclude and 'rels' in self._rel_data:
            if len(self._rel_data['rels']) < 2:
                errors.setdefault(NON_FIELD_ERRORS, []).append(
                    "You have to set minimum 2 rels.")

        try:
            super().clean_fields(exclude)
        except ValidationError as e:
            for k, ms in e.error_dict.items():
                errors.setdefault(k, []).extend(ms)

        if errors:
            raise ValidationError(errors)


class TestOne2ManyRelModel(JSONReprMixin, models.Model):
    name = models.CharField(max_length=30)
    descr = models.TextField()
    rel = models.ForeignKey(
        TestOne2ManyModel, related_name='rels', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "TestOne2ManyRelModel"
        verbose_name_plural = "TestOne2ManyRelModels"
        ordering = ['pk']


@rest_view("/test")
class TestOne2ManyRestView(FakeViewMixin, RestView):
    default_public = True
    model = TestOne2ManyModel

    fields = ['name', VF('rels', related_fields=[
        'name', VF('descr', readonly=True)])]


urlpatterns = [
    path('api/', include(register_views(TestOne2ManyRestView))),
    path('api/', include('pfx.pfxcore.urls'))
]


@override_settings(ROOT_URLCONF=__name__)
class TestFieldsOne2Many(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')

    @classmethod
    def setUpTestData(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TestOne2ManyModel)
            schema_editor.create_model(TestOne2ManyRelModel)

    def test_meta(self):
        response = self.client.get('/api/test/meta')
        self.assertRC(response, 200)
        fields = 'fields.rels.fields'
        self.assertJE(response, f'{fields}.name.name', "name")
        self.assertJE(response, f'{fields}.name.type', "CharField")
        self.assertJE(response, f'{fields}.name.required', True)
        self.assertJE(response, f'{fields}.name.readonly.post', False)
        self.assertJE(response, f'{fields}.name.readonly.put', False)
        self.assertJE(response, f'{fields}.descr.name', "descr")
        self.assertJE(response, f'{fields}.descr.type', "TextField")
        self.assertJE(response, f'{fields}.descr.required', True)
        self.assertJE(response, f'{fields}.descr.readonly.post', True)
        self.assertJE(response, f'{fields}.descr.readonly.put', True)

    def test_get(self):
        o = TestOne2ManyModel.objects.create(name="Test")
        r1 = TestOne2ManyRelModel.objects.create(rel=o, name="R1", descr="D1")
        r2 = TestOne2ManyRelModel.objects.create(rel=o, name="R2", descr="D2")

        response = self.client.get(f'/api/test/{o.pk}')
        self.assertRC(response, 200)
        self.assertSize(response, 'rels', 2)
        self.assertJE(response, 'rels.@0.pk', r1.pk)
        self.assertJE(response, 'rels.@0.name', "R1")
        self.assertJE(response, 'rels.@0.descr', "D1")
        self.assertJE(response, 'rels.@1.pk', r2.pk)
        self.assertJE(response, 'rels.@1.name', "R2")
        self.assertJE(response, 'rels.@1.descr', "D2")

    def test_post(self):
        response = self.client.post('/api/test', dict(
            name="Test",
            rels=[dict(name="R1", descr="D1"), dict(name="R2", descr="D2")]
        ))
        self.assertRC(response, 200)
        self.assertSize(response, 'rels', 2)
        self.assertJE(response, 'rels.@0.name', "R1")
        self.assertJE(response, 'rels.@0.descr', "D1")
        self.assertJE(response, 'rels.@1.name', "R2")
        self.assertJE(response, 'rels.@1.descr', "D2")

    def test_post_field_errors(self):
        response = self.client.post('/api/test', dict(
            rels=[dict(name="R1", descr="D1"), dict(descr="D2")]
        ))
        self.assertRC(response, 422)
        self.assertEqual(
            set(response.json().keys()), {'name', 'rels::1::name'})
        self.assertJE(response, 'name', ["This field cannot be blank."])
        self.assertJE(
            response, 'rels::1::name', ["This field cannot be null."])

        response = self.client.post('/api/test', dict(
            rels=[dict(descr="D1")]
        ))
        self.assertRC(response, 422)
        self.assertEqual(
            set(response.json().keys()), {'__all__', 'name', 'rels::0::name'})
        self.assertJE(response, '__all__', ["You have to set minimum 2 rels."])
        self.assertJE(response, 'name', ["This field cannot be blank."])
        self.assertJE(
            response, 'rels::0::name', ["This field cannot be null."])

    def test_put(self):
        o = TestOne2ManyModel.objects.create(name="Test")
        r1 = TestOne2ManyRelModel.objects.create(rel=o, name="R1", descr="D1")

        vals = self.client.get(f'/api/test/{o.pk}').json()
        vals['rels'][0]['name'] = "R1 updated"
        vals['rels'].append({'name': "R2", "descr": "D2"})

        response = self.client.put(f'/api/test/{o.pk}', vals)
        self.assertRC(response, 200)
        self.assertSize(response, 'rels', 2)
        self.assertJE(response, 'rels.@0.pk', r1.pk)
        self.assertJE(response, 'rels.@0.name', "R1 updated")
        self.assertJE(response, 'rels.@0.descr', "D1")
        self.assertJE(response, 'rels.@1.name', "R2")
        self.assertJE(response, 'rels.@1.descr', "D2")

    def test_put_field_errors(self):
        o = TestOne2ManyModel.objects.create(name="Test")
        TestOne2ManyRelModel.objects.create(rel=o, name="R1", descr="D1")
        TestOne2ManyRelModel.objects.create(rel=o, name="R2", descr="D2")

        vals = self.client.get(f'/api/test/{o.pk}').json()
        vals['name'] = ""
        vals['rels'][0]['name'] = None
        del vals['rels'][1]

        response = self.client.put(f'/api/test/{o.pk}', vals)
        self.assertRC(response, 422)
        self.assertEqual(
            set(response.json().keys()), {'__all__', 'name', 'rels::0::name'})
        self.assertJE(response, '__all__', ["You have to set minimum 2 rels."])
        self.assertJE(response, 'name', ["This field cannot be blank."])
        self.assertJE(
            response, 'rels::0::name', ["This field cannot be null."])

    def test_put_delete(self):
        o = TestOne2ManyModel.objects.create(name="Test")
        r1 = TestOne2ManyRelModel.objects.create(rel=o, name="R1", descr="D1")
        r2 = TestOne2ManyRelModel.objects.create(rel=o, name="R2", descr="D2")
        TestOne2ManyRelModel.objects.create(rel=o, name="R3", descr="D3")

        vals = self.client.get(f'/api/test/{o.pk}').json()
        del vals['rels'][2]

        response = self.client.put(f'/api/test/{o.pk}', vals)
        self.assertRC(response, 200)
        self.assertSize(response, 'rels', 2)
        self.assertJE(response, 'rels.@0.pk', r1.pk)
        self.assertJE(response, 'rels.@0.name', "R1")
        self.assertJE(response, 'rels.@0.descr', "D1")
        self.assertJE(response, 'rels.@1.pk', r2.pk)
        self.assertJE(response, 'rels.@1.name', "R2")
        self.assertJE(response, 'rels.@1.descr', "D2")
