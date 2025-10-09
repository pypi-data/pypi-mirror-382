
from datetime import date
from unittest.mock import MagicMock, patch

from django.db import connection
from django.test import TestCase, override_settings

from pfx.pfxcore.shortcuts import permissions
from pfx.pfxcore.test import APIClient, MockBoto3Client, TestAssertMixin
from tests.models import Author, Book, User


class TestPermissions(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')
        with connection.cursor() as cursor:
            cursor.execute("create extension if not exists unaccent;")

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='user',
            email="user@example.com",
            password='test',
            first_name="Test",
            last_name="User",
            is_superuser=False)
        cls.admin = User.objects.create_user(
            username='admin',
            email="admin@example.com",
            password='test',
            first_name="Test",
            last_name="Admin",
            is_superuser=True)

        cls.author1 = Author.objects.create(
            first_name='John Ronald Reuel',
            last_name='Tolkien',
            slug='jrr-tolkien')
        cls.author1_book1 = Book.objects.create(
            author=cls.author1,
            name="The Hobbit",
            pub_date=date(1937, 1, 1))
        cls.author2 = Author.objects.create(
            first_name='Philip Kindred',
            last_name='Dick',
            science_fiction=True,
            slug='philip-k-dick')
        cls.author3 = Author.objects.create(
            first_name='Isaac',
            last_name='Asimov',
            science_fiction=True,
            slug='isaac-asimov')

    def test_get_list_admin(self):
        self.client.login(username='admin')

        response = self.client.get('/api/perms/authors?items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)

    def test_get_list_user(self):
        self.client.login(username='user')

        response = self.client.get('/api/perms/authors?items=1&count=1')
        self.assertRC(response, 403)

        self.user.user_permissions.add(*permissions('tests.view_author'))

        response = self.client.get('/api/perms/authors?items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)

    def test_get_detail_admin(self):
        self.client.login(username='admin')

        response = self.client.get(f'/api/perms/authors/{self.author1.pk}')
        self.assertRC(response, 200)

    def test_get_detail_user(self):
        self.client.login(username='user')

        response = self.client.get(f'/api/perms/authors/{self.author1.pk}')
        self.assertRC(response, 403)

        self.user.user_permissions.add(*permissions('tests.view_author'))

        response = self.client.get(f'/api/perms/authors/{self.author1.pk}')
        self.assertRC(response, 200)

    def test_get_by_slug_admin(self):
        self.client.login(username='admin')

        response = self.client.get(
            f'/api/perms/authors/slug/{self.author1.slug}')
        self.assertRC(response, 200)

    def test_get_by_slug_user(self):
        self.client.login(username='user')

        response = self.client.get(
            f'/api/perms/authors/slug/{self.author1.slug}')
        self.assertRC(response, 403)

        self.user.user_permissions.add(*permissions('tests.view_author'))

        response = self.client.get(
            f'/api/perms/authors/slug/{self.author1.slug}')
        self.assertRC(response, 200)

    def test_create_admin(self):
        self.client.login(username='admin')

        response = self.client.post(
            '/api/perms/authors', dict(
                first_name='New',
                last_name='Author',
                slug='new'))
        self.assertRC(response, 200)

    def test_create_user(self):
        self.client.login(username='user')

        response = self.client.post(
            '/api/perms/authors', dict(
                first_name='New',
                last_name='Author',
                slug='new'))
        self.assertRC(response, 403)

        self.user.user_permissions.add(*permissions('tests.add_author'))

        response = self.client.post(
            '/api/perms/authors', dict(
                first_name='New',
                last_name='Author',
                slug='new'))
        self.assertRC(response, 200)

    def test_update_admin(self):
        self.client.login(username='admin')

        response = self.client.put(
            f'/api/perms/authors/{self.author1.pk}', dict(last_name='UPDATED'))
        self.assertRC(response, 200)

    def test_update_user(self):
        self.client.login(username='user')

        response = self.client.put(
            f'/api/perms/authors/{self.author1.pk}', dict(last_name='UPDATED'))
        self.assertRC(response, 403)

        self.user.user_permissions.add(*permissions('tests.change_author'))

        response = self.client.put(
            f'/api/perms/authors/{self.author1.pk}', dict(last_name='UPDATED'))
        self.assertRC(response, 200)

    def test_delete_admin(self):
        self.client.login(username='admin')

        response = self.client.delete(f'/api/perms/authors/{self.author3.pk}')
        self.assertRC(response, 200)

    def test_delete_user(self):
        self.client.login(username='user')

        response = self.client.delete(f'/api/perms/authors/{self.author3.pk}')
        self.assertRC(response, 403)

        self.user.user_permissions.add(*permissions('tests.delete_author'))

        response = self.client.delete(f'/api/perms/authors/{self.author3.pk}')
        self.assertRC(response, 200)

    @override_settings(
        STORAGE_S3_AWS_REGION="fake-region",
        STORAGE_S3_AWS_ACCESS_KEY="FAKE",
        STORAGE_S3_AWS_SECRET_KEY="FAKE-SECRET",
        STORAGE_S3_AWS_S3_BUCKET="dragonfly.fake",
        STORAGE_S3_AWS_GET_URL_EXPIRE=300,
        STORAGE_S3_AWS_PUT_URL_EXPIRE=300)
    @patch("boto3.client", MagicMock(return_value=MockBoto3Client()))
    def test_media_api_admin(self):
        self.client.login(username='admin')

        response = self.client.get(
            f'/api/perms/books/{self.author1_book1.pk}/cover/upload-url/'
            'cover.png?content-type=image/png')
        self.assertRC(response, 200)

        response = self.client.put(
            f'/api/perms/books/{self.author1_book1.pk}', dict(
                cover=response.json_content['file']))
        self.assertRC(response, 200)

        response = self.client.get(
            f'/api/perms/books/{self.author1_book1.pk}/cover')
        self.assertRC(response, 200)

    @override_settings(
        STORAGE_S3_AWS_REGION="fake-region",
        STORAGE_S3_AWS_ACCESS_KEY="FAKE",
        STORAGE_S3_AWS_SECRET_KEY="FAKE-SECRET",
        STORAGE_S3_AWS_S3_BUCKET="dragonfly.fake",
        STORAGE_S3_AWS_GET_URL_EXPIRE=300,
        STORAGE_S3_AWS_PUT_URL_EXPIRE=300)
    @patch("boto3.client", MagicMock(return_value=MockBoto3Client()))
    def test_media_api_user(self):
        self.client.login(username='user')

        response = self.client.get(
            f'/api/perms/books/{self.author1_book1.pk}/cover/upload-url/'
            'cover.png?content-type=image/png')
        self.assertRC(response, 403)

        self.user.user_permissions.add(*permissions('tests.change_book'))

        response = self.client.get(
            f'/api/perms/books/{self.author1_book1.pk}/cover/upload-url/'
            'cover.png?content-type=image/png')
        self.assertRC(response, 200)

        response = self.client.put(
            f'/api/perms/books/{self.author1_book1.pk}', dict(
                cover=response.json_content['file']))
        self.assertRC(response, 200)

        response = self.client.get(
            f'/api/perms/books/{self.author1_book1.pk}/cover')
        self.assertRC(response, 403)

        self.user.user_permissions.add(*permissions('tests.view_book'))

        response = self.client.get(
            f'/api/perms/books/{self.author1_book1.pk}/cover')
        self.assertRC(response, 200)

    def test_custom_get_admin(self):
        self.client.login(username='admin')

        response = self.client.get('/api/perms/authors/custom')
        self.assertRC(response, 200)

    def test_custom_get_user(self):
        self.client.login(username='user')

        response = self.client.get('/api/perms/authors/custom')
        self.assertRC(response, 403)

        self.user.user_permissions.add(*permissions('tests.view_author'))

        response = self.client.get('/api/perms/authors/custom')
        self.assertRC(response, 200)

    def test_custom_put_admin(self):
        self.client.login(username='admin')

        response = self.client.put('/api/perms/authors/custom')
        self.assertRC(response, 200)

    def test_custom_put_user(self):
        self.client.login(username='user')

        response = self.client.put('/api/perms/authors/custom')
        self.assertRC(response, 403)

        self.user.user_permissions.set(permissions('tests.change_author'))

        response = self.client.put('/api/perms/authors/custom')
        self.assertRC(response, 403)

        self.user.user_permissions.set(permissions(
            'tests.can_customize_author'))

        response = self.client.put('/api/perms/authors/custom')
        self.assertRC(response, 403)

        self.user.user_permissions.set(permissions(
            'tests.change_author', 'tests.can_customize_author'))

        response = self.client.put('/api/perms/authors/custom')
        self.assertRC(response, 200)
