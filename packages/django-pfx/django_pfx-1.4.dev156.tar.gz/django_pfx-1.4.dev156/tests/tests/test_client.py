from django.db import connection, models
from django.http import HttpResponse
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import include, path

from pfx.pfxcore import register_views
from pfx.pfxcore.decorator import rest_api, rest_view
from pfx.pfxcore.http import JsonResponse
from pfx.pfxcore.models import JSONReprMixin
from pfx.pfxcore.test import APIClient, TestAssertMixin
from pfx.pfxcore.views import RestView
from tests.models import User
from tests.views import FakeViewMixin


class TestModel(JSONReprMixin, models.Model):
    name = models.CharField("Name", max_length=30)

    class Meta:
        verbose_name = "TestModel"
        verbose_name_plural = "TestModels"
        ordering = ['name', 'pk']

    def __str__(self):
        return self.name


@rest_view("/test")
class TestRestView(FakeViewMixin, RestView):
    default_public = True
    model = TestModel

    @rest_api('/locale', method='get')
    def locale(self, *args, **kwargs):
        return JsonResponse(
            dict(locale=self.request.META.get('HTTP_X_CUSTOM_LANGUAGE')))

    @rest_api('/<int:id>', method='patch')
    def patch(self, *args, **kwargs):
        return self._put(*args, **kwargs)

    @rest_api('', method='options')
    def options(self, *args, **kwargs):
        return HttpResponse(
            headers=dict(
                Allow=', '.join(self._allowed_methods()),
                Content_Length=0
            ))

    @rest_api('', method='head')
    def head(self, *args, **kwargs):
        response = self._get_list(*args, **kwargs)
        response.content = ''
        return response

    @rest_api('', method='trace')
    def trace(self, *args, **kwargs):
        return HttpResponse(content_type='message/http')


urlpatterns = [
    path('api/', include(register_views(TestRestView))),
    path('api/', include('pfx.pfxcore.urls'))
]


@override_settings(ROOT_URLCONF=__name__)
class TestApiClient(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')

    # @classmethod
    # def setUpClass(cls):

    #     super(TestApiClient, cls).setUpClass()

    @classmethod
    def setUpTestData(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(TestModel)
        cls.user = User.objects.create_user(
            username='jrr.tolkien',
            email="jrr.tolkien@oxford.com",
            password='RIGHT PASSWORD',
            first_name='John Ronald Reuel',
            last_name='Tolkien',
        )
        cls.test = TestModel.objects.create(name='test')

    def test_login(self):
        self.assertTrue(
            self.client.login(
                username='jrr.tolkien',
                password='RIGHT PASSWORD'))
        self.assertTrue(self.client.token)

    def test_logout(self):
        self.client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')
        self.assertTrue(self.client.token)
        self.client.logout()
        self.assertFalse(self.client.token)

    def test_login_cookie(self):
        cookie_client = APIClient(default_locale='en')
        self.assertTrue(
            cookie_client.login(
                username='jrr.tolkien',
                password='RIGHT PASSWORD'))
        self.assertTrue(cookie_client.token)

    def test_logout_cookie(self):
        cookie_client = APIClient(default_locale='en')
        self.assertTrue(
            cookie_client.login(
                username='jrr.tolkien',
                password='RIGHT PASSWORD'))
        self.assertTrue(cookie_client.token)
        cookie_client.logout()
        self.assertFalse(cookie_client.token)

    def test_locale(self):
        response = self.client.get(
            '/api/test/locale')
        self.assertRC(response, 200)
        self.assertEqual(response.headers.get('Content-Language'), 'en')

        response = self.client.get(
            '/api/test/locale', locale='fr')
        self.assertRC(response, 200)
        self.assertEqual(response.headers.get('Content-Language'), 'fr')

    def test_get(self):
        response = self.client.get(f'/api/test/{self.test.pk}')
        self.assertRC(response, 200)

    def test_head(self):
        response = self.client.head('/api/test')
        self.assertRC(response, 200)

    def test_post(self):
        response = self.client.post(
            '/api/test', dict(name='test2'))
        self.assertRC(response, 200)

    def test_put(self):
        response = self.client.put(
            f'/api/test/{self.test.pk}', dict(name='test2'))
        self.assertRC(response, 200)

    def test_delete(self):
        response = self.client.delete(
            f'/api/test/{self.test.pk}')
        self.assertRC(response, 200)

    def test_patch(self):
        response = self.client.patch(
            f'/api/test/{self.test.pk}', dict(test='value'))
        self.assertRC(response, 200)

    def test_options(self):
        response = self.client.options(
            '/api/test')
        self.assertRC(response, 200)

    def test_trace(self):
        response = self.client.trace(
            '/api/test')
        self.assertRC(response, 200)
