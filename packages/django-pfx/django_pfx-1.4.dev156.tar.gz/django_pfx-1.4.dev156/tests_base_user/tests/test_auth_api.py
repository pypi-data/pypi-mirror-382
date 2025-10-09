import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.test import TransactionTestCase, override_settings

import jwt
from freezegun import freeze_time

from pfx.pfxcore.models import PFXUser
from pfx.pfxcore.test import APIClient, TestAssertMixin

logger = logging.getLogger(__name__)


class AuthAPITest(TestAssertMixin, TransactionTestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')
        self.cookie_client = APIClient(default_locale='en', with_cookie=True)
        self.user1 = PFXUser.objects.create_user(
            username='jrr.tolkien',
            email="jrr.tolkien@oxford.com",
            password='RIGHT PASSWORD',
            first_name='John Ronald Reuel',
            last_name='Tolkien',
        )

    def test_invalid_login(self):
        response = self.client.post(
            '/api/auth/login', {
                'username': 'jrr.tolkien',
                'password': 'WRONG PASSWORD'})
        self.assertRC(response, 422)

    def test_emtpy_login(self):
        response = self.client.post(
            '/api/auth/login', {})
        self.assertRC(response, 422)

    @override_settings(PFX_TOKEN_SHORT_VALIDITY={'minutes': 30})
    def test_valid_login(self):
        with freeze_time("2023-05-01 08:00:00"):
            response = self.client.post(
                '/api/auth/login', {
                    'username': 'jrr.tolkien',
                    'password': 'RIGHT PASSWORD'})

            self.assertRC(response, 200)
            token = self.get_val(response, 'token')
            headers = jwt.get_unverified_header(token)
            self.assertEqual(headers['pfx_user_pk'], self.user1.pk)
            decoded = jwt.decode(
                token, self.user1.password + settings.PFX_SECRET_KEY,
                algorithms="HS256")
            self.assertTrue(
                datetime.utcnow() + timedelta(minutes=25) <
                datetime.utcfromtimestamp(decoded['exp'])
                < datetime.utcnow() + timedelta(minutes=35))
