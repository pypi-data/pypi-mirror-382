from django.contrib.auth.hashers import make_password
from django.test import TestCase

from pfx.pfxcore.test import APIClient, TestAssertMixin
from tests_custom_user.models import User


class TestApi(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username='user',
            password=make_password('test'))

    def test_get_user(self):
        self.client.login(username='user')

        response = self.client.get(f'/api/users/{self.user.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'username', 'user')
