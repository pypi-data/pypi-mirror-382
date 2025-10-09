from django.test import TestCase

from pfx.pfxcore.models import PFXUser
from pfx.pfxcore.shortcuts import permissions
from pfx.pfxcore.test import APIClient, TestAssertMixin


class TestApi(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')

    @classmethod
    def setUpTestData(cls):
        cls.user = PFXUser.objects.create_user(
            username='user',
            password='test',
            first_name='Test',
            last_name='User',
        )

    def test_get_user(self):
        self.client.login(username='user')

        response = self.client.get(f'/api/users/{self.user.pk}')
        self.assertRC(response, 403)

        self.user.user_permissions.add(*permissions('pfxcore.view_pfxuser'))

        response = self.client.get(f'/api/users/{self.user.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'username', 'user')
