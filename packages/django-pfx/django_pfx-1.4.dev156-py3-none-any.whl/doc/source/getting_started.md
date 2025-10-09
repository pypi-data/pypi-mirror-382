# Getting Started with PFX

## Install django pfx

Using pip
```bash
pip install django-pfx
```

## Configuration

Add pfxcore to the installed app

```python
INSTALLED_APPS = [
    'pfx.pfxcore',
]
```

## Create your services

### Model class
Create a simple model class.
```python
from django.db import models


class Book(models.Model):
    BOOK_TYPES = [
        ('science_fiction', 'Science Fiction'),
        ('heroic_fantasy', 'Heroic Fantasy'),
        ('detective', 'Detective')]

    title = models.CharField("Title", max_length=30)
    author = models.CharField("Author", max_length=150)
    type = models.CharField("Type", max_length=20, choices=BOOK_TYPES)
    pub_date = models.DateField("Pub Date")
    created_at = models.DateField("Created at", auto_now_add=True)

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return f"{self.name}"

```

### Views
Create a new view
```python
from pfx.pfxcore.decorator import rest_view
from pfx.pfxcore.views import RestView

from book.models import Book


@rest_view("/books")
class BookRestView(RestView):
    default_public = True
    queryset = Book.objects
    fields = ['title', 'author', 'type', 'pub_date', 'created_at']
```

### URLs
Register the url in urls.py.
```python
from django.urls import path, include
from pfx.pfxcore import register_views


from book import views

apipatterns = register_views(views.BookRestView)

urlpatterns = [
    path('api/', include(apipatterns)),
]
```

You now have a fully functional public API for the book objet.

### Test the API
The next step is to create a test class to test your new API.
PFX provides [some tools](testing.md) to ease the testing.

```python
from datetime import date
from django.test import TransactionTestCase
from pfx.pfxcore.test import TestAssertMixin, APIClient

from book.models import Book, Author

class BookTestClass(TestAssertMixin, TransactionTestCase):

    @classmethod
    def setUpTestData(cls):
        # create some test data
        cls.author = Author.objects.create(
            first_name='Isaac',
            last_name='Asimov')
        cls.book1 = Book.objects.create(
            author=cls.author,
            title="The Caves of Steel",
            type='science_fiction',
            pub_date=date(1954, 1, 1))
        cls.book2 = Book.objects.create(
            author=cls.author,
            title="The Naked Sun",
            type='science_fiction',
            pub_date=date(1957, 1, 1))

    def test_get_book_list(self):
        client = APIClient()
        response = client.get('/api/books')

        # assert response status is 200 OK
        self.assertRC(response, 200)
        # assert number of item returned
        self.assertSize(response, 'items', 2)
        # test the author of the second item is Asimov
        self.assertJE(response, 'items.@1.author.pk', self.author.pk)

    def test_get_book(self):
        client = APIClient()
        response = client.get(f'/api/books/{self.book2.pk}')

        # assert response status is 200 OK
        self.assertRC(response, 200)
        # assert json content of the response
        self.assertJE(response, 'title', "The Naked Sun")
        self.assertJE(response, 'pub_date', "1957-01-01")

    def test_create_book(self):
        client = APIClient()
        response = client.post(
            '/api/books/',dict(
                title="The Robots of Dawn",
                author=self.author,
                type='science_fiction',
                pub_date=date(1983, 1, 1)
            ))
        self.assertRC(response, 200)
        self.assertJE(response, 'title', "The Robots of Dawn")

    def test_create_book_validation(self):
        client = APIClient()
        # make a post request
        response = client.post(
            '/api/books/',dict(
                title=None,
                author=self.author,
                type='science_fiction',
                pub_date=date(1983, 1, 1)
            ))
        self.assertRC(response, 422)
        self.assertJE(
            response, 'title.@0', "This field cannot be null.")

    def test_update_book(self):
        client = APIClient()
        response = client.put(
            f'/api/books/{self.book2.pk}',dict(
                title="The Robots of Dawn",
                pub_date=date(1983, 1, 1),
            ))
        self.assertRC(response, 200)
        self.assertJE(response, 'title', "The Robots of Dawn")

    def test_delete_book(self):
        client = APIClient()
        response = client.delete(
            f'/api/books/{self.book2.pk}')
        self.assertRC(response, 200)

        books = Book.objects.filter(pk=self.book2.pk)
        self.assertEqual(books.count(), 0)

```
