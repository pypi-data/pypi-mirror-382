from datetime import date
from unittest.mock import patch

import django
from django.test import TestCase
from django.test.utils import override_settings

from pfx.pfxcore.test import (
    APIClient,
    TestAssertMixin,
    format_request,
    get_url,
)
from tests.models import Author


class TestTools(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')

    @classmethod
    def setUpTestData(cls):
        cls.author1 = Author.objects.create(
            first_name='John Ronald Reuel',
            last_name='Tolkien',
            slug='jrr-tolkien')
        pass

    @patch('builtins.print')
    def test_key_error(self, mock_print):
        response = self.client.get('/api/authors/meta/list')
        self.assertRC(response, 200)
        with self.assertRaises(Exception):
            self.assertJE(response, 'items.@0.name-not-exists', 'not exists')

    @patch('builtins.print')
    def test_index_error(self, mock_print):
        response = self.client.get('/api/authors/meta/list')
        self.assertRC(response, 200)
        with self.assertRaises(Exception):
            self.assertJE(response, 'items.@99.name', 'gender')

    @patch('builtins.print')
    def test_print_response(self, mock_print):
        response = self.client.get(f'/api/authors/{self.author1.pk}')

        self.assertRC(response, 200)
        response.print()

        self.assertEqual(mock_print.call_count, 1)
        printed = mock_print.call_args.args[0]
        self.assertIn(
            '******************** http response ********************', printed)
        self.assertIn('Status: 200 OK', printed)
        self.assertIn('Headers: ', printed)
        if django.VERSION[0] >= 4:
            self.assertIn("""  Content-Type: application/json
  Content-Length: %s
  X-Content-Type-Options: nosniff
  Referrer-Policy: same-origin
  Cross-Origin-Opener-Policy: same-origin
  Vary: Accept-Language
  Content-Language: en
""" % (response.headers['Content-Length']), printed)
        else:
            self.assertIn("""  Content-Type: application/json
  Content-Length: %s
  X-Content-Type-Options: nosniff
  Referrer-Policy: same-origin
  Vary: Accept-Language
  Content-Language: en
""" % (response.headers['Content-Length']), printed)
        self.assertIn('Content: ', printed)
        self.assertIn('"books": []', printed)
        self.assertIn('"create_comment": "",', printed)
        self.assertIn(f'"created_at": "{date.today()}"', printed)
        self.assertIn('"first_name": "John Ronald Reuel",', printed)
        self.assertIn(""""gender": {
        "label": "Male",
        "value": "male"
    },""", printed)
        self.assertIn('"last_name": "Tolkien",', printed)
        self.assertIn('"name_length": 25,', printed)
        self.assertIn(f'"pk": {self.author1.pk},', printed)
        self.assertIn('"resource_name": "John Ronald Reuel Tolkien",', printed)
        self.assertIn('"slug": "jrr-tolkien",', printed)
        self.assertIn('"update_comment": ""', printed)
        self.assertIn('"meta": {},', printed)

    @patch('builtins.print')
    @override_settings(PFX_TEST_MODE=True)
    def test_print_request(self, mock_print):
        self.client.post(
            '/api/authors?useless=param&second=param',
            dict(first_name="Arthur Charles",
                 last_name="Clarke"),
            print_request=True)
        self.assertEqual(mock_print.call_count, 1)
        printed = mock_print.call_args.args[0]
        self.assertIn(
            '******************** http request ********************', printed)
        self.assertIn('Path: /api/authors', printed)
        self.assertIn('Method: POST', printed)
        self.assertIn('Query params:', printed)
        self.assertIn('  useless: param', printed)
        self.assertIn('  second: param', printed)
        self.assertIn('Headers: ', printed)
        self.assertIn('  Cookie: ', printed)
        self.assertIn('  Content-Length: 55', printed)
        self.assertIn('  Content-Type: application/json', printed)
        self.assertIn('  X-Custom-Language: en', printed)
        self.assertIn('  X-Print-Request: true', printed)
        self.assertIn('Content: ', printed)
        self.assertIn('"first_name": "Arthur Charles",', printed)
        self.assertIn('"last_name": "Clarke"', printed)

        self.client.get(
            "/api/authors?gender=female", print_request=True)

        self.assertEqual(mock_print.call_count, 2)
        printed = mock_print.call_args.args[0]
        self.assertIn(
            '******************** http request ********************', printed)
        self.assertIn('Path: /api/authors', printed)
        self.assertIn('Method: GET', printed)
        self.assertIn('Query params:', printed)
        self.assertIn('  gender: female', printed)
        self.assertIn('Headers: ', printed)
        self.assertIn('  Cookie: ', printed)
        self.assertIn('  X-Custom-Language: en', printed)
        self.assertIn('  X-Print-Request: true', printed)
        self.assertIn('Content: ', printed)
        self.assertIn('Request is empty', printed)

    @patch('builtins.print')
    @override_settings(PFX_TEST_MODE=True)
    def test_format_request_edge_cases(self, mock_print):
        self.assertEqual(format_request(None), "Request is null")

        self.client.generic(
            method='POST', path='/api/authors',
            data='{"incorrect":"json format',
            content_type='application/json', print_request=True)

        self.assertEqual(mock_print.call_count, 1)
        printed = mock_print.call_args.args[0]
        self.assertIn('Content: ', printed)
        self.assertIn('Json Decode Error', printed)
        self.assertIn("""b'{"incorrect":"json format'""", printed)

        self.client.generic(
            method='POST', path='/api/authors',
            data='Plain text',
            content_type='text/plain', print_request=True)

        self.assertEqual(mock_print.call_count, 2)
        printed = mock_print.call_args.args[0]
        self.assertIn('Content: ', printed)
        self.assertIn("""b'Plain text'""", printed)

    def test_get_url(self):
        self.assertEqual(
            get_url('/test/thing'),
            '/test/thing')
        self.assertEqual(
            get_url('/test/thing', mode="test"),
            '/test/thing?mode=test')
        self.assertEqual(
            get_url('/test/thing', mode="qwertz", uid=12345, other="string"),
            '/test/thing?mode=qwertz&uid=12345&other=string')
