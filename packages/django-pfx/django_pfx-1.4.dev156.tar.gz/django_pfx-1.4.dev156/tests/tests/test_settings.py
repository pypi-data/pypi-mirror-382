from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from pfx.pfxcore.test import TestAssertMixin
from pfx.pfxcore.views import AuthenticationView
from tests.models import User


class TestSettings(TestAssertMixin, TestCase):

    @override_settings(PFX_SECRET_KEY="")
    def test_mandatory_pfx_secret_key(self):
        user = User.objects.create_user(
            username='user',
            email="user@example.com",
            password='test',
            first_name='User',
            last_name='Test')

        with self.assertRaises(ImproperlyConfigured):
            AuthenticationView()._prepare_token(user)
