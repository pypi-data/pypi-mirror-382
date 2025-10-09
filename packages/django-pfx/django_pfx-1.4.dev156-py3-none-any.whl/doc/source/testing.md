# Testing
Django PFX provides tools to ease API testing.

## APIClient
APIClient is a utility class to request the API in test classes.
It inherits from DjangoClient and add
locale and json response management.

If the response content_type is `application/json`,
the response contains a json_content
attributes with the deserialized json content.

### Locale

If your application is internationalized,
you can pass a default locale to the client
so that each request header contains
the HTTP_X_CUSTOM_LANGUAGE attribute with the locale.

Example :
```python
from pfx.pfxcore.test import APIClient

client = APIClient(default_locale='en_GB')
```
Each request to a service can also override the locale.
Example :
```python
from pfx.pfxcore.test import APIClient

client = APIClient()
response = client.get('/api/authors', locale='fr_CH')
```


### GET
Send a get request.

Example :
```python
from pfx.pfxcore.test import APIClient

client = APIClient()
response = client.get('/api/authors')
```

### POST
Send a post request with content type 'application/json'.

Example :
```python
from pfx.pfxcore.test import APIClient

client = APIClient()
response = client.post(
    '/api/authors', {
        'first_name': 'Arthur Charles',
        'last_name': 'Clarke'})
```

### PUT
Send a put request with content type 'application/json'.

Example :
```python
from pfx.pfxcore.test import APIClient

client = APIClient()
response = self.client.put(
    f'/api/authors/{author_pk}',
    {'first_name': 'J. R. R.',
     'last_name': 'Tolkien',
     'slug': 'j-r-r-tolkien'})
```

### DELETE
Send a delete request with content type 'application/json'.

Example :
```python
from pfx.pfxcore.test import APIClient

client = APIClient()
response = client.delete(
    f'/api/authors/{author_pk}')
```

### Login
If you use PFX authentication views you can use this login method.

Once you called login, you can call any other method
listed above, the authentication token will be sent with the requests.

Example :
```python
from pfx.pfxcore.test import APIClient

client = APIClient()
client.login(
    username='jrr.tolkien',
    password='thepwd')

client.get('/api/authors')  # authenticated request.
```

## TestAssertMixin
TestAssertMixin provides useful method for your test class.

### assertRC
Test the response code of a response.
It takes two parameters, the response and the expected status code.

Example :
```python
from django.test import TransactionTestCase
from pfx.pfxcore.test import TestAssertMixin, APIClient

class ATestClass(TestAssertMixin, TransactionTestCase):

    def a_test(self):
        client = APIClient()
        response = client.post(
            '/api/authors', {
            'first_name': 'Arthur Charles',
            'last_name': 'Clarke'})
        self.assertRC(response, 200)
```

### get_val

Get a value for a python dictionary or a json HTTP response by a string path key.
The src parameter can be a Python dictionary or an object with `json_content` attribute.
For instance if you have a response like
```python
{
    "author": {
        "pk": 2,
        "resource_name": "Philip Kindred Dick"
    },
    "name": "A Scanner Darkly",
    "pk": 6,
}
```
you can reach the author pk by providing `"author.pk"` as the key.

get_val also allows to specify the index in an array.
The syntax is `"@index"`.

For instance if you want the pk of the author of the
third item in an array of books you can specify `"items.@2.author.pk"`

Example :
```python
from django.test import TransactionTestCase
from pfx.pfxcore.test import TestAssertMixin, APIClient

class ATestClass(TestAssertMixin, TransactionTestCase):

    def a_test(self):
        client = APIClient()
        response = client.get('/api/books')
        author_pk = self.get_val(response, 'items.@2.author.pk')
```

### assertJE
Test the value of a dictionary property (using `get_val`).
It takes 3 parameters, the source, the key and the expected value.

Example :
```python
from django.test import TransactionTestCase
from pfx.pfxcore.test import TestAssertMixin, APIClient

class ATestClass(TestAssertMixin, TransactionTestCase):

    def a_test(self):
        client = APIClient()
        response = client.get('/api/books')
        self.assertJE(response, 'items.@2.author.pk', self.author1.pk)
```

### assertNJE
`AssertNJE` is the same as `AssertJE`, but it tests that the value is not equal.

### assertJEExists
Assert the path exists in the source.

### assertJENotExists
Assert the path does not exist in the source.

### assertSize
Test the size of a value (if the value is a collection).

### assertJIn
Test that an element is part of a collection value.

## Print Request
For debugging purposes Django Pfx allows you to print
the request as the server receives it.

You need to set the `PFX_TEST_MODE` setting to `True` to enable this feature.

One way to do it is to rely on the launch parameter to
see if you have launched `./manage.py test`.
```python
import sys

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    PFX_TEST_MODE=True
```

Then, you have to add `print_request=True` in your APIClient call.

Example :
```python
from pfx.pfxcore.test import APIClient

client = APIClient()
response = client.post('/api/autors?demo=true',
                       dict(first_name="Arthur Charles",
                            last_name="Clarke"),
                       print_request=True)
```

It will print the following output to the console.

```text
******************** http request ********************
Path: /api/authors
Method: POST
Query params:
  demo: true
Headers:
  Cookie:
  Content-Length: 55
  Content-Type: application/json
  X-Custom-Language: en
  X-Print-Request: true
Content:
{
    "first_name": "Arthur Charles",
    "last_name": "Clarke"
}
*******************************************************

```

## Print Response
You can use the `print` method of the response to print
the content of the response in the console.

Example :
```python
from pfx.pfxcore.test import APIClient

client = APIClient()
response = client.get('/api/books')
response.print()
```

It will print the following output to the console.

```text
*********************http response*********************
Status :  200 OK
Headers :
  Content-Type: application/json
  Content-Length: 258
  X-Content-Type-Options: nosniff
  Referrer-Policy: same-origin
  Vary: Accept-Language
  Content-Language: en

Content :
{
    "author": {
        "pk": 2,
        "resource_name": "Philip Kindred Dick"
    },
    "created_at": "2022-01-15",
    "meta": {
        "message": "Book A Scanner Darkly updated."
    },
    "name": "A Scanner Darkly",
    "pk": 6,
    "pub_date": "1977-01-01",
    "resource_name": "A Scanner Darkly",
}
*******************************************************
```

## TestPermsAssertMixin

This test mixin can be used to test permissions on services with multiple users.

Create multiple users in `setUpTestData` and add a method for each service
you want to test.

You can test the response status code or the response list count for items list responses.

Example :
```python
from pfx.pfxcore.test import TestPermsAssertMixin, APIClient

class BookPermsAPITest(TestPermsAssertMixin):
    def setUp(self):
        self.client = APIClient(with_cookie=True)

    @classmethod
    def setUpTestData(cls):
        # Create your users here

    def list(self):
        # Create a book
        return self.client.get('/api/books?items=1&count=1')

    def get(self):
        # book = … (create a book)
        return self.client.get(f'/api/books/{book.pk}')

    def post(self):
        return self.client.post('/api/books', dict(
            name="Test new"))

    def put(self):
        return self.client.put(
            f'/api/books/{self.organization.pk}', dict(
                name="Updated"))

    def delete(self):
        # book = … (create a book)
        return self.client.delete(f'/api/books/{book.pk}')

    USER_TESTS = {
        "admin@user.org": dict(
            list=200, list__count=1, get=200,
            post=200, put=200, delete=200),
        "user@user.org": dict(
            list=200, list__count=1, get=200,
            post=403, put=403, delete=403),
    }
```
