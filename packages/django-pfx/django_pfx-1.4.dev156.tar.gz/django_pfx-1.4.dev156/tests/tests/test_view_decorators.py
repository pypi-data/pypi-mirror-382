from django.test import TestCase

from pfx.pfxcore.test import APIClient, TestAssertMixin
from tests.views import BaseRestView, IllegalPriorityRestView


class ViewDecoratorTest(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_method_not_allowed(self):
        response = self.client.put('/api/authors')
        self.assertRC(response, 405)

    def test_method_not_allowed_if_non_http_method(self):
        response = self.client.generic('ILLEGAL', '/api/authors')
        self.assertEqual(response.status_code, 405)

    def test_method_not_allowed_if_not_exists(self):
        response = self.client.get('/api/does-not-exists')
        self.assertRC(response, 405)

    def test_explicit_priority(self):
        # With default priority, string > untyped.
        response = self.client.get(
            '/api/authors/priority/dynamic')
        self.assertRC(response, 200)
        self.assertJE(response, 'value', 'str:dynamic')

        # With default priority, static string > dynamic.
        response = self.client.get(
            '/api/authors/priority/default')
        self.assertRC(response, 200)
        self.assertJE(response, 'value', 'static:default')

        # With default priority, string > static string.
        response = self.client.get(
            '/api/authors/priority/hello')
        self.assertRC(response, 200)
        self.assertJE(response, 'value', 'str:hello')

        # With default priority, path is used
        response = self.client.get(
            '/api/authors/priority/hello/there')
        self.assertRC(response, 200)
        self.assertJE(response, 'value', 'path:hello/there')

        # With default priority, static path > dynamic path
        response = self.client.get(
            '/api/authors/priority/default/path')
        self.assertRC(response, 200)
        self.assertJE(response, 'value', 'static:default_path')

        # With low priority, string is used.
        response = self.client.get(
            '/api/authors/priority/priority-less')
        self.assertRC(response, 200)
        self.assertJE(response, 'value', 'str:priority-less')

        # With high priority, priorized is used.
        response = self.client.get(
            '/api/authors/priority/priority-more')
        self.assertRC(response, 200)
        self.assertJE(response, 'value', 'static:more')

    def test_illegal_priority(self):
        with self.assertRaises(Exception):
            IllegalPriorityRestView.as_urlpatterns()

    def test_path_order(self):
        paths = [
            '/api/xxx/<int:param>',
            '/api/xxx/me',
            '/api/xxx/<param>/other/test',
            '/api/xxx/<param>',
            '/api/xxx/<int:param>/other',
            '/api/xxx/<param>/other/<param2>']
        sorted_paths = sorted(paths, key=lambda p: BaseRestView._path_order(
            p, dict(priority=0)), reverse=True)
        self.assertEqual(sorted_paths, [
            '/api/xxx/me',
            '/api/xxx/<int:param>/other',
            '/api/xxx/<int:param>',
            '/api/xxx/<param>/other/test',
            '/api/xxx/<param>/other/<param2>',
            '/api/xxx/<param>'])

    def test_path_order_path(self):
        paths = [
            '/api/xxx/<path:path>',
            '/api/xxx/<param>/test']
        sorted_paths = sorted(paths, key=lambda p: BaseRestView._path_order(
            p, dict(priority=0)), reverse=True)
        self.assertEqual(sorted_paths, [
            '/api/xxx/<param>/test',
            '/api/xxx/<path:path>'])
