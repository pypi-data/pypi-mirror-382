from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.db import connection
from django.test import TestCase, override_settings

from pfx.pfxcore.test import APIClient, MockBoto3Client, TestAssertMixin
from tests.models import Author, Book, BookType


@override_settings(
    STORAGE_LOCAL_ROOT='/tmp/django-pfx-filestore',
    STORAGE_LOCAL_X_ACCEL_REDIRECT=False)
class BasicAPITest(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')
        with connection.cursor() as cursor:
            cursor.execute("create extension if not exists unaccent;")

    @classmethod
    def setUpTestData(cls):
        cls.type_sf = BookType.objects.create(
            name="Science fiction", slug="sf")
        cls.type_fantastique = BookType.objects.create(
            name="Fantastique", slug="fantastique")
        cls.type_fantasy = BookType.objects.create(
            name="Fantastique", slug="fantastique")
        cls.type_romance = BookType.objects.create(
            name="Romance", slug="romance")

        cls.author1 = Author.objects.create(
            first_name='John Ronald Reuel',
            last_name='Tolkien',
            slug='jrr-tolkien')
        cls.author1_book1 = Book.objects.create(
            author=cls.author1,
            name="The Hobbit",
            pub_date=date(1937, 1, 1))
        cls.author1_book2 = Book.objects.create(
            author=cls.author1,
            name="The Fellowship of the Ring",
            pub_date=date(1954, 1, 1))
        cls.author1_book3 = Book.objects.create(
            author=cls.author1,
            name="The Two Towers",
            pub_date=date(1954, 1, 1))
        cls.author1_book4 = Book.objects.create(
            author=cls.author1,
            name="The Return of the King",
            pub_date=date(1955, 1, 1))

        cls.author2 = Author.objects.create(
            first_name='Philip Kindred',
            last_name='Dick',
            science_fiction=True,
            slug='philip-k-dick')
        cls.author2.types.set([cls.type_sf, cls.type_fantastique])

        cls.author3 = Author.objects.create(
            first_name='Isaac',
            last_name='Asimov',
            science_fiction=True,
            slug='isaac-asimov')
        cls.author3.types.set([cls.type_sf])
        cls.author3_book1 = Book.objects.create(
            author=cls.author3,
            name="The Caves of Steel",
            pub_date=date(1954, 1, 1),
            pages=224,
            rating=4.6)
        cls.author3_book2 = Book.objects.create(
            author=cls.author3,
            name="The Naked Sun",
            pages=304,
            pub_date=date(1957, 1, 1))
        cls.author3_book3 = Book.objects.create(
            author=cls.author3,
            name="The Robots of Dawn",
            pub_date=date(1983, 1, 1))

        cls.author4 = Author.objects.create(
            first_name='Joanne',
            last_name='Rowling',
            science_fiction=False,
            gender='female',
            slug='j-k-rowling')

    def test_get_list(self):
        response = self.client.get('/api/authors?items=1&count=1')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)

    def test_get_list_extra_meta(self):
        response = self.client.get('/api/authors-extra-meta?items=1&count=1')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)
        self.assertJE(response, 'meta.test', "Hello world")

    @override_settings(PFX_MAX_LIST_RESULT_SIZE=10)
    def test_get_list_global_limit(self):
        for i in range(10):
            Book.objects.create(
                author=self.author1,
                name=f"Book {i}",
                pub_date=date(1900, 1, 1))

        response = self.client.get('/api/books?items=1&count=1')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 17)
        self.assertSize(response, 'items', 10)

        response = self.client.get(
            '/api/books?subset=pagination&page-size=50&items=1&count=1')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 17)
        self.assertJE(response, 'meta.subset.page_size', 10)
        self.assertSize(response, 'items', 10)

        response = self.client.get(
            '/api/books?subset=offset&page-size=50&items=1&count=1')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 17)
        self.assertJE(response, 'meta.subset.limit', 10)
        self.assertSize(response, 'items', 10)

    def test_get_list_order_asc(self):
        response = self.client.get('/api/authors?order=last_name')
        self.assertRC(response, 200)

        names = [i['last_name'] for i in response.json_content['items']]
        self.assertEqual(names, ['Asimov', 'Dick', 'Rowling', 'Tolkien'])

    def test_get_list_order_desc(self):
        response = self.client.get('/api/authors?order=-last_name')
        self.assertRC(response, 200)

        names = [i['last_name'] for i in response.json_content['items']]
        self.assertEqual(names, ['Tolkien', 'Rowling', 'Dick', 'Asimov'])

    def test_get_list_order_multi(self):
        response = self.client.get('/api/authors?order=gender,last_name')
        self.assertRC(response, 200)

        names = [i['last_name'] for i in response.json_content['items']]
        self.assertEqual(names, ['Rowling', 'Asimov', 'Dick', 'Tolkien'])

    def test_get_list_order_multi_desc(self):
        response = self.client.get('/api/authors?order=gender,-last_name')
        self.assertRC(response, 200)

        names = [i['last_name'] for i in response.json_content['items']]
        self.assertEqual(names, ['Rowling', 'Tolkien', 'Dick', 'Asimov'])

    def test_get_list_order_invalid(self):
        response = self.client.get('/api/authors?order=invalid_field')
        self.assertRC(response, 400)

        self.assertIn(
            "Cannot resolve keyword 'invalid_field' into field.",
            self.get_val(response, 'message'))

    def test_get_list_order_with_order_mapping(self):
        response = self.client.get(
            f'/api/books?author={self.author3.pk}&order=pages')
        self.assertRC(response, 200)
        pages = [
            self.get_val(item, 'pages')
            for item in self.get_val(response, 'items')]
        self.assertEqual(pages, [None, 224, 304])

        response = self.client.get(
            f'/api/books?author={self.author3.pk}&order=%2Bpages')
        self.assertRC(response, 200)
        pages = [
            self.get_val(item, 'pages')
            for item in self.get_val(response, 'items')]
        self.assertEqual(pages, [None, 224, 304])

        response = self.client.get(
            f'/api/books?author={self.author3.pk}&order=-pages')
        self.assertRC(response, 200)
        pages = [
            self.get_val(item, 'pages')
            for item in self.get_val(response, 'items')]
        self.assertEqual(pages, [304, 224, None])

    def test_search_list(self):
        response = self.client.get('/api/authors?search=isaac&items=1&count=1')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)
        self.assertJE(response, 'items.@0.first_name', 'Isaac')
        self.assertJE(response, 'items.@0.last_name', 'Asimov')
        self.assertJE(response, 'items.@0.gender.value', 'male')
        self.assertJE(response, 'items.@0.gender.label', 'Male')

        response = self.client.get(
            '/api/authors?search=isaac&search=tolkien&items=1&count=1')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 2)

    def test_meta_list(self):
        response = self.client.get('/api/authors/meta/list')
        self.assertRC(response, 200)
        self.assertJE(response, 'model.app', 'tests')
        self.assertJE(response, 'model.name', 'author')
        self.assertJE(response, 'model.object', 'Author')

        self.assertJE(response, 'filters.@0.name', 'book_type')
        self.assertJE(response, 'filters.@0.items', [
            {
                'empty_value': False,
                "is_group": False,
                "label": "Science Fiction",
                "name": "science_fiction",
                "technical": True,
                "type": "BooleanField"
            },
            {
                'empty_value': True,
                "is_group": False,
                "label": "Heroic Fantasy",
                "name": "heroic_fantasy",
                "technical": False,
                "type": "BooleanField"
            },
            {
                'empty_value': False,
                "is_group": False,
                "label": "Types",
                "name": "types",
                "related_model": "BookType",
                "api": "/book-types",
                "technical": False,
                "type": "ModelObject"
            }
        ])
        self.assertJE(response, 'filters.@1.name', 'custom')
        self.assertJE(response, 'filters.@1.items', [
            {
                'empty_value': False,
                "is_group": False,
                "label": "Last Name",
                "name": "last_name",
                "technical": False,
                "type": "BooleanField"
            },
            {
                'empty_value': False,
                "is_group": False,
                "label": "First Name",
                "name": "first_name",
                "technical": False,
                "type": "CharField"
            },
            {
                "choices": [
                    {
                        "label": "Male",
                        "value": "male"
                    },
                    {
                        "label": "Female",
                        "value": "female"
                    }
                ],
                'empty_value': False,
                "is_group": False,
                "label": "Gender",
                "name": "gender",
                "technical": False,
                "type": "CharField"
            },
            {
                "choices": [
                    {
                        "label": "Tolkien",
                        "value": "Tolkien"
                    },
                    {
                        "label": "Asimov",
                        "value": "Asimov"
                    }
                ],
                'empty_value': False,
                "is_group": False,
                "label": "Tolkien or Asimov",
                "name": "last_name_choices",
                "technical": False,
                "type": "CharField"
            }
        ])

        response = self.client.get('/api/books/meta/list?filters=1&orders=1')
        self.assertRC(response, 200)

        self.assertJE(response, 'filters.@0.items.@0', {
            "empty_value": False,
            "is_group": False,
            "label": "Author",
            "name": "author",
            "related_model": "Author",
            "api": "/authors",
            "technical": False,
            "type": "ModelObject"
        })

        self.assertJIn(response, 'orders', 'pk')
        self.assertJIn(response, 'orders', 'name')
        self.assertJIn(response, 'orders', 'author')
        self.assertJIn(response, 'orders', 'author__pk')
        self.assertJIn(response, 'orders', 'author__first_name')

    def test_filter_func_bool(self):
        response = self.client.get(
            '/api/authors?heroic_fantasy=true&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)
        self.assertJE(response, 'items.@0.resource_name',
                                'John Ronald Reuel Tolkien')

        response = self.client.get(
            '/api/authors?heroic_fantasy=false&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)

        response = self.client.get(
            '/api/authors?heroic_fantasy=false&heroic_fantasy=true'
            '&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)

    def test_filter_func_date(self):
        response = self.client.get(
            '/api/books?pub_date_gte=1955-01-01&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)

    def test_filter_func_char_choices(self):
        response = self.client.get(
            '/api/authors?last_name_choices=Tolkien&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)

    def test_model_filter_bool(self):
        response = self.client.get(
            '/api/authors?science_fiction=true&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 2)

        response = self.client.get(
            '/api/authors?science_fiction=invalid&items=1&count=1')
        self.assertRC(response, 400)
        self.assertJE(
            response, 'message', "Invalid value for Science Fiction filter")

    def test_model_filter_char(self):
        response = self.client.get(
            '/api/authors?first_name=Isaac&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)
        self.assertJE(response, 'items.@0.first_name', "Isaac")

    def test_model_filter_integer(self):
        response = self.client.get('/api/books?pages=224&items=1&count=1')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)
        self.assertJE(response, 'items.@0.name', "The Caves of Steel")

        response = self.client.get('/api/books?pages=invalid&items=1&count=1')
        self.assertRC(response, 400)
        self.assertJE(response, 'message', "Invalid value for Pages filter")

    def test_model_filter_float(self):
        response = self.client.get('/api/books?rating=4.6&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)
        self.assertJE(response, 'items.@0.name', "The Caves of Steel")

        response = self.client.get('/api/books?rating=invalid&items=1&count=1')
        self.assertRC(response, 400)
        self.assertJE(response, 'message', "Invalid value for Rating filter")

    def test_model_filter_date(self):
        response = self.client.get(
            '/api/books?pub_date=1954-01-01&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)

        response = self.client.get(
            '/api/books?pub_date=invalid&items=1&count=1')
        self.assertRC(response, 400)
        self.assertJE(response, 'message', "Invalid value for Pub Date filter")

    def test_model_filter_manytomany(self):
        response = self.client.get(
            f'/api/authors?types={self.type_romance.pk}&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 0)

        response = self.client.get(
            f'/api/authors?types={self.type_fantastique.pk}&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)
        self.assertJE(response, 'items.@0.pk', self.author2.pk)

        response = self.client.get(
            f'/api/authors?types={self.type_sf.pk}&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 2)
        self.assertJE(response, 'items.@0.pk', self.author3.pk)
        self.assertJE(response, 'items.@1.pk', self.author2.pk)

        # Check multiple values filtered with OR condition.
        response = self.client.get(
            f'/api/authors?types={self.type_fantastique.pk}'
            f'&types={self.type_romance.pk}&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)
        self.assertJE(response, 'items.@0.pk', self.author2.pk)

        response = self.client.get(
            f'/api/authors?types={self.type_fantastique.pk}'
            f'&types={self.type_sf.pk}&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 2)
        self.assertJE(response, 'items.@0.pk', self.author3.pk)
        self.assertJE(response, 'items.@1.pk', self.author2.pk)

        response = self.client.get(
            '/api/authors?types=invalid&items=1&count=1')
        self.assertRC(response, 400)
        self.assertJE(response, 'message', "Invalid value for Types filter")

    def test_model_filter_decimal(self):
        # TODO: Wait Decimal implementation
        pass

    def test_model_filter_foreign_key(self):
        response = self.client.get(
            f'/api/books?author={self.author3.pk}&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)
        for item in response.json_content['items']:
            self.assertEqual(item['author']['pk'], self.author3.pk)

        response = self.client.get(
            '/api/books?author=invalid&items=1&count=1')
        self.assertRC(response, 400)
        self.assertJE(response, 'message', "Invalid value for Author filter")

    def test_model_filter_foreign_key_null(self):
        book_type = BookType.objects.create(
            name="Epic Fantasy",
            slug="epic-fantasy")
        self.author1_book1.type = book_type
        self.author1_book1.save()

        response = self.client.get(
            f'/api/books?author={self.author1.pk}&type={book_type.pk}'
            '&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 1)

        response = self.client.get(
            f'/api/books?author={self.author1.pk}&type=null&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)
        for item in response.json_content['items']:
            self.assertEqual(item['type'], None)
        response = self.client.get(
            f'/api/books?author={self.author1.pk}&type=0&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 0)
        response = self.client.get(
            f'/api/books?author={self.author1.pk}&type=&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)
        for item in response.json_content['items']:
            self.assertEqual(item['type'], None)

        response = self.client.get(
            f'/api/books?author={self.author1.pk}&'
            f'type={book_type.pk}&type=null&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)
        for item in response.json_content['items']:
            self.assertTrue(
                item['type'] is None or item['type']['pk'] == book_type.pk)

    def test_model_filter_foreign_key_text_search(self):
        response = self.client.get(
            '/api/books?author*=asimov&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)

        # Test multiple values
        response = self.client.get(
            '/api/books?author*=asimov&author*=tolkien&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 7)

        # Test empty search
        response = self.client.get(
            '/api/books?author*=&items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 7)

    def test_model_filter_char_choices(self):
        response = self.client.get('/api/authors?gender=male&items=1&count=1')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 3)

    def test_model_filter_func_bool(self):
        response = self.client.get(
            '/api/authors?last_name=true&items=1&count=1')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)

    def test_get_list_without_pagination(self):
        response = self.client.get('/api/authors?count=1')

        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)

    def test_get_list_with_subset(self):
        for i in range(1, 11):
            Author.objects.create(
                first_name='Vladimir',
                last_name=f'Ottor {i}',
                science_fiction=True,
                slug=f'vald-ottor-{i}')

        response = self.client.get('/api/authors?subset=offset&limit=5')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.subset.offset', 0)
        self.assertJE(response, 'meta.subset.count', 14)
        item4_pk = response.json_content['items'][3]['pk']

        response = self.client.get(
            '/api/authors?subset=offset&offset=3&limit=5')
        self.assertRC(response, 200)
        # With offset 3 the first item must be the same as the 4th
        # in the request with offest 0.
        self.assertJE(response, 'items.@0.pk', item4_pk)
        self.assertJE(response, 'meta.subset.count', 14)

    def test_select_list(self):
        response = self.client.get(
            '/api/authors?mode=select&items=true&limit=10')
        self.assertRC(response, 200)
        self.assertSize(response, 'items', 4)

    def test_select_list_search(self):
        response = self.client.get(
            '/api/authors?mode=select&subset=offset&limit=10&search=Isaac')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.subset.count', 1)
        self.assertJE(response, 'items.@0.resource_name', "Isaac Asimov")

    def test_select_list_max(self):
        response = self.client.get(
            '/api/authors?mode=select&subset=offset&items=true&limit=3')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.subset.count', 4)
        self.assertSize(response, 'items', 3)

    def test_meta_service(self):
        response = self.client.get('/api/authors/meta')
        self.assertRC(response, 200)
        self.assertJE(response, 'model.app', 'tests')
        self.assertJE(response, 'model.name', 'author')
        self.assertJE(response, 'model.object', 'Author')
        self.assertJE(response, 'fields.first_name.type', 'CharField')
        self.assertJE(response, 'fields.first_name.name', 'First Name')
        self.assertJE(response, 'fields.last_name.type', 'CharField')
        self.assertJE(response, 'fields.last_name.name', 'Last Name')
        self.assertJE(response, 'fields.books.type', 'ModelObjectList')
        self.assertJE(response, 'fields.books.name', 'Books')
        self.assertJE(response, 'fields.created_at.type', 'DateField')
        self.assertJE(response, 'fields.created_at.name', 'Created at')
        self.assertJE(response, 'fields.name_length.type', 'IntegerField')
        self.assertJE(response, 'fields.name_length.name', 'Name Length')
        self.assertJE(response, 'fields.types.type', 'ModelObjectList')
        self.assertJE(response, 'fields.types.name', 'Types')
        response = self.client.get('/api/books/meta')
        self.assertJE(response, 'fields.author.type', 'ModelObject')
        self.assertJE(response, 'fields.author.model', 'tests.Author')
        self.assertJE(response, 'fields.author.api', '/authors')
        self.assertJE(
            response, 'fields.read_time.type', 'MinutesDurationField')
        self.assertJE(response, 'fields.read_time.name', 'Read Time')

    def test_meta_service_fr(self):
        response = self.client.get('/api/authors/meta', locale='fr')
        self.assertRC(response, 200)
        self.assertJE(response, 'fields.first_name.type', 'CharField')
        self.assertJE(response, 'fields.first_name.name', 'Prénom')
        self.assertJE(response, 'fields.last_name.type', 'CharField')
        self.assertJE(response, 'fields.last_name.name', 'Nom')
        response = self.client.get('/api/books/meta')
        self.assertJE(
            response, 'fields.read_time.type', 'MinutesDurationField')
        self.assertJE(response, 'fields.read_time.name', 'Read Time')

    def test_get_detail_by_id(self):
        response = self.client.get(f'/api/authors/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'first_name', self.author1.first_name)
        self.assertJE(response, 'last_name', self.author1.last_name)
        self.assertJE(response, 'name_length', 25)
        self.assertJE(response, 'gender.value', 'male')
        self.assertJE(response, 'gender.label', 'Male')

    def test_get_detail_by_slug(self):
        response = self.client.get(f'/api/authors/slug/{self.author1.slug}')
        self.assertRC(response, 200)
        self.assertJE(response, 'first_name', self.author1.first_name)
        self.assertJE(response, 'last_name', self.author1.last_name)
        self.assertJE(response, 'name_length', 25)
        self.assertJE(response, 'gender.value', 'male')
        self.assertJE(response, 'gender.label', 'Male')

    def test_get_date_format(self):
        response = self.client.get(f'/api/books/{self.author1_book1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'pub_date', '1937-01-01')

    def test_get_detail_with_rel_object(self):
        response = self.client.get(f'/api/books/{self.author3_book1.pk}')

        self.assertRC(response, 200)
        self.assertJE(response, 'author.pk', self.author3.pk)
        self.assertJE(response, 'author.resource_name', "Isaac Asimov")
        self.assertJE(response, 'author.resource_slug', "isaac-asimov")
        self.assertJEExists(response, 'author.resource_slug')
        self.assertJENotExists(response, 'author.hello')
        self.assertJENotExists(response, 'author.last_name')

    def test_get_detail_with_rel_object_custom(self):
        response = self.client.get(
            f'/api/books-custom-author/{self.author3_book1.pk}')

        self.assertRC(response, 200)
        self.assertJE(response, 'author.pk', self.author3.pk)
        self.assertJE(response, 'author.resource_name', "Isaac Asimov")
        self.assertJE(response, 'author.resource_slug', "isaac-asimov")
        self.assertJE(response, 'author.hello', "World")
        self.assertJE(response, 'author.last_name', "Asimov")

    def test_get_detail_manytomany(self):
        response = self.client.get(f'/api/authors/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertSize(response, 'types', 0)

        response = self.client.get(f'/api/authors/{self.author2.pk}')
        self.assertRC(response, 200)
        self.assertSize(response, 'types', 2)
        self.assertJE(response, 'types.@0.pk', self.type_sf.pk)
        self.assertJE(response, 'types.@1.pk', self.type_fantastique.pk)

        response = self.client.get(f'/api/authors/{self.author3.pk}')
        self.assertRC(response, 200)
        self.assertSize(response, 'types', 1)
        self.assertJE(response, 'types.@0.pk', self.type_sf.pk)

    def test_get_non_existant_record(self):
        response = self.client.get('/api/authors/999999')
        self.assertRC(response, 404)

    def test_get_non_existant_record_by_slug(self):
        response = self.client.get('/api/authors/slug/not-existent')
        self.assertRC(response, 404)

    def test_create(self):
        response = self.client.post(
            '/api/authors', dict(
                first_name='Arthur Charles',
                last_name='Clarke',
                name_length=1,
                gender='male',
                create_comment='CREATE COMMENT',
                update_comment='UPDATE COMMENT',
                website=None,
                slug='arthur-c-clarke',
                types=[self.type_sf.pk, dict(pk=self.type_fantastique.pk)]))

        self.assertRC(response, 200)
        self.assertJE(response, 'first_name', 'Arthur Charles')
        self.assertJE(response, 'last_name', 'Clarke')
        self.assertJE(response, 'gender.value', 'male')
        self.assertJE(response, 'gender.label', 'Male')
        self.assertJE(response, 'create_comment', 'CREATE COMMENT')
        self.assertNJE(response, 'update_comment', 'UPDATE COMMENT')
        self.assertJE(response, 'website', '')
        self.assertSize(response, 'types', 2)
        self.assertJE(response, 'types.@0.pk', self.type_sf.pk)
        self.assertJE(response, 'types.@1.pk', self.type_fantastique.pk)

    def test_create_file(self):
        response = self.client.post('/api/books', dict(
            name="Test Book",
            author=self.author1.pk,
            pub_date='2000-01-01',
            local_file=dict(
                name='test.txt',
                base64='data:text/plain;charset=utf-8;'
                'base64,VGVzdCBjb250ZW50')))
        book_pk = self.get_val(response, 'pk')
        self.assertRC(response, 200)
        self.assertJE(response, 'local_file.content-length', '12')
        self.assertJE(response, 'local_file.content-type', 'text/plain')
        self.assertJE(
            response, 'local_file.key',
            f"Book/{book_pk}/bca20547e94049e1ffea27223581c567022a5774.txt")
        self.assertJE(response, 'local_file.name', 'test.txt')
        self.assertJE(
            response, 'local_file.url', f"/books/{book_pk}/local_file")
        self.assertTrue(Path(
            f'/tmp/django-pfx-filestore/Book/{book_pk}/'
            'bca20547e94049e1ffea27223581c567022a5774.txt').exists())

        # Replace file
        response = self.client.put(f'/api/books/{book_pk}', dict(
            local_file=dict(
                name='test2.txt',
                base64='data:text/plain;charset=utf-8;'
                'base64,TmV3IGNvbnRlbnQ=')))
        self.assertRC(response, 200)
        self.assertJE(
            response, 'local_file.key',
            f"Book/{book_pk}/af9f06b2b3b1546ac44f4a02994d0ef09e074b91.txt")
        self.assertJE(response, 'local_file.name', 'test2.txt')
        self.assertFalse(Path(
            f'/tmp/django-pfx-filestore/Book/{book_pk}/'
            'bca20547e94049e1ffea27223581c567022a5774.txt').exists())
        self.assertTrue(Path(
            f'/tmp/django-pfx-filestore/Book/{book_pk}/'
            'af9f06b2b3b1546ac44f4a02994d0ef09e074b91.txt').exists())

        # Delete file
        response = self.client.put(f'/api/books/{book_pk}', dict(
            local_file=None))
        self.assertRC(response, 200)
        self.assertJE(response, 'local_file', None)
        self.assertFalse(Path(
            f'/tmp/django-pfx-filestore/Book/{book_pk}/'
            'af9f06b2b3b1546ac44f4a02994d0ef09e074b91.txt').exists())

    def test_create_null_values(self):
        response = self.client.post(
            '/api/books', dict(
                name="Test Book",
                author=self.author1.pk,
                type=None,
                pub_date='2000-01-01',
                pages=None,
                rating=None,
                reference=None,
                read_time=None))
        self.assertRC(response, 200)

    def test_create_enum(self):
        response = self.client.post(
            '/api/authors', {
                'first_name': 'Arthur Charles',
                'last_name': 'Clarke',
                'name_length': 1,
                'gender': {'value': 'male'},
                'slug': 'arthur-c-clarke'})

        self.assertRC(response, 200)
        self.assertJE(response, 'first_name', 'Arthur Charles')
        self.assertJE(response, 'last_name', 'Clarke')
        self.assertJE(response, 'gender.value', 'male')
        self.assertJE(response, 'gender.label', 'Male')

    def test_create_enum_bad_value(self):
        response = self.client.post(
            '/api/authors', {
                'first_name': 'Arthur Charles',
                'last_name': 'Clarke',
                'name_length': 1,
                'gender': {'value': 'writer'},
                'slug': 'arthur-c-clarke'})

        self.assertRC(response, 422)
        self.assertJE(
            response, 'gender.@0', "Value 'writer' is not a valid choice.")

    def test_create_unique_custom_message(self):
        response = self.client.post(
            '/api/books', dict(
                name="The Hobbit",
                author=self.author1.pk))
        self.assertRC(response, 422)
        self.assertJE(
            response, '__all__.@0',
            'The Hobbit already exists for John Ronald Reuel Tolkien')

    def test_create_invalid_date(self):
        response = self.client.post(
            '/api/books', dict(
                name="The Silmarillion",
                author=self.author1.pk,
                pub_date="19777-09-15"))
        self.assertRC(response, 422)
        self.assertJE(
            response, 'pub_date.@0',
            '“19777-09-15” value has an invalid date format. '
            'It must be in YYYY-MM-DD format.')

    def test_update(self):
        response = self.client.put(
            f'/api/authors/{self.author1.pk}',
            {'pk': self.author2.pk,  # pk and id must be ignored
             'created_at': '2021-01-01',  # created_at must be ignored because
                                          # it is a readonly field.
             'first_name': 'J. R. R.',
             'name_length': 1,
             'gender': 'female',
             'create_comment': 'CREATE COMMENT UPDATED',
             'update_comment': 'UPDATE COMMENT UPDATED',
             'slug': 'j-r-r-tolkien'})  # slug must be updated})

        self.assertRC(response, 200)
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.first_name, 'J. R. R.')
        self.assertEqual(self.author1.last_name, 'Tolkien')
        self.assertEqual(self.author1.slug, 'j-r-r-tolkien')
        self.assertEqual(self.author1.gender, 'female')
        self.assertNotEqual(self.author1.created_at, '2021-01-01 11:30:00')
        self.assertNotEqual(
            self.author1.create_comment, 'CREATE COMMENT UPDATED')
        self.assertEqual(
            self.author1.update_comment, 'UPDATE COMMENT UPDATED')

        response = self.client.put(
            f'/api/authors/{self.author1.pk}', {'gender': {'value': 'male'}})
        self.assertRC(response, 200)
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.gender, 'male')

    def test_update_manytomny(self):
        self.assertEqual(self.author1.types.count(), 0)

        response = self.client.put(
            f'/api/authors/{self.author1.pk}', dict(
                types=[self.type_fantasy.pk]))
        self.assertRC(response, 200)
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.types.count(), 1)
        self.assertEqual(self.author1.types.all()[0].pk, self.type_fantasy.pk)

        response = self.client.put(
            f'/api/authors/{self.author1.pk}', dict(types=[]))
        self.assertRC(response, 200)
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.types.count(), 0)

    def test_update_enum_bad_value(self):
        response = self.client.put(
            f'/api/authors/{self.author1.pk}', {
                'gender': {'value': 'writer'}})

        self.assertRC(response, 422)
        self.assertJE(
            response, 'gender.@0', "Value 'writer' is not a valid choice.")

    def test_empty_number_fields(self):
        response = self.client.post(
            '/api/books', {
                'name': 'The Fellowship of the Ring, Deluxe Edition',
                'author': self.author1.pk,
                'pub_date': '1954-07-29',
                'pages': '',
                'rating': '',
            })
        self.assertRC(response, 200)
        self.assertJE(response, 'pages', None)
        self.assertJE(response, 'rating', None)

        response = self.client.post(
            '/api/books', {
                'name': 'The Two Towers, Deluxe Edition',
                'author': self.author1.pk,
                'pub_date': '1954-07-29',
                'pages': 500,
                'rating': 5.35,
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'pages', 500)
        self.assertJE(response, 'rating', 5.35)

        response = self.client.put(
            f"/api/books/{response.json_content['pk']}", {
                'pages': '',
                'rating': '',
            })
        self.assertRC(response, 200)
        self.assertJE(response, 'pages', None)
        self.assertJE(response, 'rating', None)

        response = self.client.put(
            f"/api/books/{response.json_content['pk']}", {
                'pages': 600,
                'rating': 6.34,
            })
        self.assertRC(response, 200)
        self.assertJE(response, 'pages', 600)
        self.assertJE(response, 'rating', 6.34)

    def test_delete(self):
        response = self.client.delete(
            f'/api/authors/{self.author2.pk}')

        self.assertRC(response, 200)

        author = Author.objects.filter(pk=self.author2.pk)
        self.assertEqual(author.count(), 0)

    def test_delete_with_wrong_key(self):
        response = self.client.delete(
            '/api/authors/99999')
        self.assertRC(response, 404)

    def test_create_with_foreignkey(self):
        response = self.client.post(
            '/api/books', {
                'name': 'The Fellowship of the Ring, Deluxe Edition',
                'author': self.author1.pk,
                'pub_date': '1954-07-29',
                'created_at': '1954-07-29',
            })
        self.assertRC(response, 200)
        self.assertJE(
            response, 'name', 'The Fellowship of the Ring, Deluxe Edition')
        self.assertJE(response, 'author.pk', self.author1.pk)
        self.assertJE(response, 'pub_date', '1954-07-29')
        self.assertNJE(response, 'created_at', '1954-07-29')

    def test_create_with_foreignkey_resource(self):
        response = self.client.post(
            '/api/books', {
                'name': 'The Fellowship of the Ring, Deluxe Edition',
                'author': {
                    'pk': self.author1.pk,
                    'resource_name': "Author One"},
                'pub_date': '1954-07-29',
                'created_at': '1954-07-29',
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'author.pk', self.author1.pk)

    def test_create_with_wrong_foreignkey(self):
        response = self.client.post(
            '/api/books', {
                'name': 'The Fellowship of the Ring, Deluxe Edition',
                'author': 999999,
                'pub_date': '1954-07-29',
                'created_at': '1954-07-29',
            })
        self.assertRC(response, 422)
        self.assertJE(response, 'author', ['Author not found.'])

    def test_update_with_foreignkey(self):
        response = self.client.put(
            f'/api/books/{self.author1_book2.pk}', {
                'name': 'The Two Towers, Deluxe Edition',
                'pub_date': '1954-11-11',
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'name', 'The Two Towers, Deluxe Edition')
        self.assertJE(response, 'author.pk', self.author1.pk)
        self.assertJE(response, 'pub_date', '1954-11-11')

        response = self.client.put(
            f'/api/books/{self.author1_book2.pk}', {
                'name': 'The Man in the High Castle',
                'author': self.author2.pk,
                'author_id': self.author3.pk,  # must be ignored
                'pub_date': '1962-10-01',
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'name', 'The Man in the High Castle')
        self.assertJE(response, 'author.pk', self.author2.pk)
        self.assertJE(response, 'pub_date', '1962-10-01')

        response = self.client.put(
            f'/api/books/{self.author1_book2.pk}', {
                'name': 'A Scanner Darkly',
                'author': {
                    'pk': self.author2.pk,
                    'resource_name': 'Philip Kindred Dick'},
                'pub_date': '1977-01-01',
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'name', 'A Scanner Darkly')
        self.assertJE(response, 'author.pk', self.author2.pk)
        self.assertJE(response, 'pub_date', '1977-01-01')

    def test_update_with_wrong_key_and_foreignkey(self):
        response = self.client.put(
            '/api/books/99999', {
                'name': 'The Two Towers',
                'pub_date': '1954-11-11'})
        self.assertRC(response, 404)

        response = self.client.put(
            f'/api/books/{self.author1_book2.pk}', {
                'name': 'The Two Towers',
                'author': 999999,
                'pub_date': '1954-11-11'})
        self.assertRC(response, 422)
        self.assertJE(response, 'author', ['Author not found.'])

    def test_delete_with_foreignkey(self):
        response = self.client.delete(
            f'/api/authors/{self.author1.pk}')

        self.assertRC(response, 400)
        self.author1_book2.refresh_from_db()

    def test_create_validation(self):
        response = self.client.post(
            '/api/books', {
                'name': '',
                'pub_date': '1954-07-29',
                'created_at': '1954-07-29',
            })

        self.assertRC(response, 422)
        self.assertJE(response, 'name',
                      ['This field cannot be blank.'])
        self.assertJE(response, 'author',
                      ['This field cannot be null.'])

    def test_update_validation(self):
        response = self.client.put(
            f'/api/books/{self.author1_book2.pk}', {
                'name': '',
                'pub_date': '1954-11-11',
            })

        self.assertRC(response, 422)
        self.assertJE(response, 'name',
                      ['This field cannot be blank.'])

    def test_create_related_field(self):
        response = self.client.post(
            '/api/books', {
                'name': 'The Fellowship of the Ring, Deluxe Edition',
                'author': self.author1.pk,
                'author__last_name': "Teulkien",
                'pub_date': '1954-07-29',
                'created_at': '1954-07-29',
            })
        self.assertRC(response, 200)
        self.assertJE(
            response, 'name', 'The Fellowship of the Ring, Deluxe Edition')
        self.assertJE(response, 'author.pk', self.author1.pk)
        self.assertJE(response, 'pub_date', '1954-07-29')
        self.assertNJE(response, 'created_at', '1954-07-29')
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.last_name, "Tolkien")

    def test_update_related_field(self):
        response = self.client.put(
            f'/api/books/{self.author1_book2.pk}', {
                'name': 'The Two Towers, Deluxe Edition',
                'author__last_name': "Teulkien",
            })
        self.assertRC(response, 200)
        self.assertJE(response, 'name', 'The Two Towers, Deluxe Edition')
        self.assertJE(response, 'author.pk', self.author1.pk)
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.last_name, "Tolkien")

    def test_custom_repr(self):
        book_type = BookType.objects.create(
            name="Epic Fantasy",
            slug="epic-fantasy",
        )
        self.author1_book2.type = book_type
        self.author1_book2.save()

        response = self.client.get(f'/api/books/{self.author1_book2.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'type.resource_name', book_type.name)
        self.assertJE(response, 'type.resource_slug', book_type.slug)

        response = self.client.get(f'/api/book-types/{book_type.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'resource_name', book_type.name)
        self.assertJE(response, 'resource_slug', book_type.slug)
        self.assertJE(response, 'name', book_type.name)
        self.assertJE(response, 'slug', book_type.slug)

    @override_settings(
        STORAGE_S3_AWS_REGION="fake-region",
        STORAGE_S3_AWS_ACCESS_KEY="FAKE",
        STORAGE_S3_AWS_SECRET_KEY="FAKE-SECRET",
        STORAGE_S3_AWS_S3_BUCKET="dragonfly.fake",
        STORAGE_S3_AWS_GET_URL_EXPIRE=300,
        STORAGE_S3_AWS_PUT_URL_EXPIRE=300)
    @patch("boto3.client", MagicMock(return_value=MockBoto3Client()))
    def test_media_field(self):
        response = self.client.get(
            f'/api/books/{self.author1_book1.pk}/cover/upload-url/'
            'cover.png?content-type=image/png')
        self.assertRC(response, 200)
        self.assertJE(response, 'file.key', "Book/1/cover.png")
        self.assertJE(response, 'file.name', "cover.png")
        self.assertJE(
            response, 'url', "http://dragonfly.fake/Book/1/cover.png")

        response = self.client.put(f'/api/books/{self.author1_book1.pk}', dict(
            cover=response.json_content['file']))
        self.assertRC(response, 200)
        self.assertJE(response, 'cover.key', "Book/1/cover.png")
        self.assertJE(response, 'cover.name', "cover.png")
        self.assertJE(response, 'cover.content-length', 1000)
        self.assertJE(response, 'cover.content-type', "image/png")

        response = self.client.get(
            f'/api/books/{self.author1_book1.pk}/cover')
        self.assertRC(response, 200)
        self.assertJE(
            response, 'url', "http://dragonfly.fake/Book/1/cover.png")

        response = self.client.get(
            f'/api/books/{self.author1_book1.pk}/cover?redirect=false')
        self.assertRC(response, 200)
        self.assertJE(
            response, 'url', "http://dragonfly.fake/Book/1/cover.png")

        response = self.client.get(
            f'/api/books/{self.author1_book1.pk}/cover?redirect=true')
        self.assertRedirects(
            response, "http://dragonfly.fake/Book/1/cover.png",
            fetch_redirect_response=False)

        with patch.object(
                MockBoto3Client, 'delete_object',
                return_value=None) as mock_delete:
            response = self.client.delete(
                f'/api/books/{self.author1_book1.pk}')
            mock_delete.assert_called_with(
                Bucket='dragonfly.fake',
                Key=f'Book/{self.author1_book1.pk}/cover.png')

    def test_annotate_meta_service(self):
        response = self.client.get('/api/authors-annotate/meta')
        self.assertRC(response, 200)
        self.assertJE(response, 'fields.first_name.type', 'CharField')
        self.assertJE(response, 'fields.first_name.name', 'First Name')
        self.assertJE(response, 'fields.books_count.type', None)
        self.assertJE(response, 'fields.books_count.name', 'books_count')
        self.assertJE(response, 'fields.books_count.readonly.post', True)
        self.assertJE(response, 'fields.books_count.readonly.put', True)
        self.assertJE(response, 'fields.books_count_annotate.type', None)
        self.assertJE(
            response, 'fields.books_count_annotate.name',
            'books_count_annotate')
        self.assertJE(
            response, 'fields.books_count_annotate.readonly.post', True)
        self.assertJE(
            response, 'fields.books_count_annotate.readonly.put', True)
        self.assertJE(response, 'fields.books_count_prop.type', None)
        self.assertJE(
            response, 'fields.books_count_prop.name', 'books_count_prop')
        self.assertJE(response, 'fields.books_count_prop.readonly.post', True)
        self.assertJE(response, 'fields.books_count_prop.readonly.put', True)

    def test_annotate_detail_service(self):
        response = self.client.get(f'/api/authors-annotate/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'books_count', 4)
        self.assertJE(response, 'books_count_annotate', 4)
        self.assertJE(response, 'books_count_prop', 4)

    def test_annotate_list_service(self):
        response = self.client.get(
            '/api/authors-annotate?items=1&count=1')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)
        self.assertJE(response, 'items.@0.last_name', 'Asimov')
        self.assertJE(response, 'items.@0.books_count', 3)
        self.assertJE(response, 'items.@0.books_count_annotate', 3)
        self.assertJE(response, 'items.@0.books_count_prop', 3)
        self.assertJE(response, 'items.@1.last_name', 'Dick')
        self.assertJE(response, 'items.@1.books_count', 0)
        self.assertJE(response, 'items.@1.books_count_annotate', 0)
        self.assertJE(response, 'items.@1.books_count_prop', 0)
        self.assertJE(response, 'items.@2.last_name', 'Rowling')
        self.assertJE(response, 'items.@2.books_count', 0)
        self.assertJE(response, 'items.@2.books_count_annotate', 0)
        self.assertJE(response, 'items.@2.books_count_prop', 0)
        self.assertJE(response, 'items.@3.last_name', 'Tolkien')
        self.assertJE(response, 'items.@3.books_count', 4)
        self.assertJE(response, 'items.@3.books_count_annotate', 4)
        self.assertJE(response, 'items.@3.books_count_prop', 4)

    def test_annotate_create_service(self):
        response = self.client.post(
            '/api/authors-annotate', {
                'first_name': 'Arthur Charles',
                'last_name': 'Clarke',
                'slug': 'arthur-c-clarke'})
        self.assertRC(response, 200)
        self.assertJE(response, 'books_count', 0)
        self.assertJE(response, 'books_count_annotate', 0)
        self.assertJE(response, 'books_count_prop', 0)

    def test_annotate_update_service(self):
        response = self.client.put(
            f'/api/authors-annotate/{self.author1.pk}', dict(
                first_name='J. R. R.',
                books_count=999,
                books_count_annotate=999,
                books_count_prop=999))

        self.assertRC(response, 200)
        self.assertJE(response, 'first_name', 'J. R. R.')
        self.assertJE(response, 'books_count', 4)
        self.assertJE(response, 'books_count_annotate', 4)
        self.assertJE(response, 'books_count_prop', 4)
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.first_name, 'J. R. R.')

    def test_fields_props_meta_service(self):
        response = self.client.get('/api/authors-fields-props/meta')
        self.assertRC(response, 200)
        self.assertJE(response, 'fields.first_name.type', 'CharField')
        self.assertJE(response, 'fields.first_name.name', 'First Name')
        self.assertJE(response, 'fields.books_count.type', 'IntegerField')
        self.assertJE(response, 'fields.books_count.name', 'Books Count')
        self.assertJE(response, 'fields.books_count.readonly.post', True)
        self.assertJE(response, 'fields.books_count.readonly.put', True)
        self.assertJE(
            response, 'fields.books_count_annotate.type', 'IntegerField')
        self.assertJE(
            response, 'fields.books_count_annotate.name',
            'Books Count (annotate)')
        self.assertJE(
            response, 'fields.books_count_annotate.readonly.post', True)
        self.assertJE(
            response, 'fields.books_count_annotate.readonly.put', True)
        self.assertJE(
            response, 'fields.books_count_prop.type', 'IntegerField')
        self.assertJE(
            response, 'fields.books_count_prop.name', 'Books Count (property)')
        self.assertJE(response, 'fields.books_count_prop.readonly.post', True)
        self.assertJE(response, 'fields.books_count_prop.readonly.put', True)

        response = self.client.get(
            '/api/authors-fields-props/meta?fields=true')
        self.assertRC(response, 200)
        self.assertJEExists(response, 'fields')
        response = self.client.get(
            '/api/authors-fields-props/meta?fields=false')
        self.assertRC(response, 200)
        self.assertJENotExists(response, 'fields')
        response = self.client.get(
            '/api/authors-fields-props/meta?other=true')
        self.assertRC(response, 200)
        self.assertJENotExists(response, 'fields')

    def test_fields_props_detail_service(self):
        response = self.client.get(
            f'/api/authors-fields-props/{self.author1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'books_count', 4)
        self.assertJE(response, 'books_count_annotate', 4)
        self.assertJE(response, 'books_count_prop', 4)

    def test_fields_props_list_service(self):
        response = self.client.get(
            '/api/authors-fields-props?items=1&count=1&order=pk')
        self.assertRC(response, 200)
        self.assertJE(response, 'meta.count', 4)
        self.assertJE(response, 'items.@0.books_count', 4)
        self.assertJE(response, 'items.@0.books_count_annotate', 4)
        self.assertJE(response, 'items.@0.books_count_prop', 4)
        self.assertJE(response, 'items.@1.books_count', 0)
        self.assertJE(response, 'items.@1.books_count_annotate', 0)
        self.assertJE(response, 'items.@1.books_count_prop', 0)

    def test_fields_props_create_service(self):
        response = self.client.post(
            '/api/authors-fields-props', {
                'first_name': 'Arthur Charles',
                'last_name': 'Clarke',
                'slug': 'arthur-c-clarke'})
        self.assertRC(response, 200)
        self.assertJE(response, 'books_count', 0)
        self.assertJE(response, 'books_count_annotate', 0)
        self.assertJE(response, 'books_count_prop', 0)

    def test_fields_props_update_service(self):
        response = self.client.put(
            f'/api/authors-fields-props/{self.author1.pk}', dict(
                first_name='J. R. R.',
                books_count=999,
                books_count_annotate=999,
                books_count_prop=999))

        self.assertRC(response, 200)
        self.assertJE(response, 'first_name', 'J. R. R.')
        self.assertJE(response, 'books_count', 4)
        self.assertJE(response, 'books_count_annotate', 4)
        self.assertJE(response, 'books_count_prop', 4)
        self.author1.refresh_from_db()
        self.assertEqual(self.author1.first_name, 'J. R. R.')

    def test_alias_field(self):
        response = self.client.get(
            f'/api/books-custom-author/{self.author3_book1.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'book_name', "The Caves of Steel")
        self.assertJE(response, 'author_last_name', "Asimov")

        response = self.client.get(
            f'/api/books-custom-author?author={self.author3.pk}')
        self.assertRC(response, 200)
        self.assertJE(response, 'items.@0.author_last_name', "Asimov")
        self.assertJEExists(response, 'items.@0.book_name')

        response = self.client.post(
            '/api/books-custom-author', dict(
                author=self.author3.pk,
                book_name="A New Book",
                pub_date='2020-01-01'
            ))
        new_book_pk = response.json_content['pk']
        self.assertRC(response, 200)
        self.assertJE(response, 'book_name', "A New Book")
        self.assertJE(response, 'author_last_name', "Asimov")

        response = self.client.put(
            f'/api/books-custom-author/{new_book_pk}', dict(
                book_name="A New Book UPDATED"))
        self.assertRC(response, 200)
        self.assertJE(response, 'book_name', "A New Book UPDATED")
        self.assertJE(response, 'author_last_name', "Asimov")
