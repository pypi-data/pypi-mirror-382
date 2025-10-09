from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test.utils import override_settings

from pfx.pfxcore.exceptions import APIError
from pfx.pfxcore.test import APIClient, TestAssertMixin
from tests.models import User


class BasicAPIErrorTest(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')

    @classmethod
    def setUpTestData(cls):
        pass

    @override_settings(DEBUG=False)
    def test_resource_not_found(self):
        response = self.client.get('/api/error/404')
        self.assertRC(response, 404)

    @override_settings(DEBUG=False)
    @patch('pfx.pfxcore.decorator.rest.logger', MagicMock())
    def test_error500(self):
        response = self.client.get('/api/error/500')
        self.assertRC(response, 500)

    def test_malformed_json(self):
        response = self.client.post(
            '/api/authors', '''{
                "first_name": "Arthur Charles",
                "last_name": "Clarke",
                "name_length": 1,
                "gender": "male,
                "slug": "arthur-c-clarke"
                }''')
        self.assertRC(response, 422)
        self.assertJE(
            response, 'message',
            "JSON Malformed Invalid control character "
            "at: line 5 column 33 (char 155)")

        User.objects.create_user(
            username='jrr.tolkien',
            email="jrr.tolkien@oxford.com",
            password='RIGHT PASSWORD',
            first_name='John Ronald Reuel',
            last_name='Tolkien',
        )

        self.client.login(
                username='jrr.tolkien',
                password='RIGHT PASSWORD')
        response = self.client.post(
            '/api/auth/change-password', '''{
                "old_password": "Wrong stuffs",
                "new_password": "Wrong stuffs",
                }''')
        self.assertRC(response, 422)
        self.assertIn(self.get_val(response, 'message'), [
            "JSON Malformed Illegal trailing comma before end "
            "of object: line 3 column 47 (char 96)",  # python >= 3.13
            "JSON Malformed Expecting property name enclosed in "
            "double quotes: line 4 column 17 (char 114)"])  # python <= 3.12

    def test_api_error_from_validation_error(self):
        error = APIError("Default", validation_error=ValidationError(
            ValidationError("Message")))
        self.assertEqual(error.data['message'], "Message")

        # If no general message, default message is used.
        error = APIError("Default", validation_error=ValidationError(
            ValidationError(dict(field1="Message"))))
        self.assertEqual(error.data['message'], "Default")
