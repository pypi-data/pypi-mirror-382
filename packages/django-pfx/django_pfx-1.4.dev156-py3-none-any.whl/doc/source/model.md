# Model

Django PFX use plain Django Models classes.

This library only provides some helpers for properties
and foreign keys representations.

## @rest_property
If you want to use properties in your model,
you have to annotate them with `@rest_property`.

Rest property takes 2 parameters, a name and
the type of the Field (CharField, IntegerField, etc.)

Rest properties can be listed as fields to be returned in list and detail views.

```python
from django.db import models
from pfx.pfxcore.decorator import rest_property

class Book(models.Model):
    name = models.CharField("Name", max_length=30)
    author = models.ForeignKey(
        'tests.Author', on_delete=models.RESTRICT,
        related_name='books', verbose_name="Author")
    pub_date = models.DateField("Pub Date")
    created_at = models.DateField("Created at", auto_now_add=True)

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return f"{self.name}"

    @rest_property("Classification", "CharField")
    def classification(self):
        return f"{self.author[0:4]}.{self.name[0:3]}"
```

## JSONReprMixin
Foreign keys are returned by [Django PFX views <pfx_views>](./pfx_views.md) as a JSON
structure with two fields : pk, resource_name

For instance for the book class, with the author foreign key  :
```python
{
    "author": {
        "pk": 1,
        "resource_name": "John Ronald Reuel Tolkien"
    },
    "created_at": "2022-01-14",
    "meta": {},
    "name": "The Fellowship of the Ring",
    "pk": 3,
    "pub_date": "1954-07-29",
    "resource_name": "The Fellowship of the Ring",
}
```

You can customize the content of this structure
by inheriting JSONReprMixin on the Model class and
by overriding the json_repr method.

For instance for the Author class :
```python
from django.db import models
from pfx.pfxcore.models import JSONReprMixin

class Author(JSONReprMixin, models.Model):
    first_name = models.CharField("First Name", max_length=30)
    last_name = models.CharField("Last Name", max_length=30)
    slug = models.SlugField("Slug", unique=True)

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def json_repr(self):
        return dict(pk=self.pk,
                    resource_slug=self.slug,
                    resource_name=str(self))
```

Which give the following result on the book service :
```python
{
    "author": {
        "pk": 1,
        "resource_name": "John Ronald Reuel Tolkien",
        "resource_slug": "john-ronald-reuel-tolkien"
    },
    "created_at": "2022-01-14",
    "meta": {},
    "name": "The Fellowship of the Ring",
    "pk": 3,
    "pub_date": "1954-07-29",
    "resource_name": "The Fellowship of the Ring",
}
```

## Not null char fields

To avoid storing a mixture of empty strings and `null` values, while automatically
converting `null` values to empty strings, you can use the following model fields:

* `NotNullCharField`
* `NotNullTextField`
* `NotNullURLField`
```python
from pfx.pfxcore.models import NotNullCharField

a_string_field = NotNullCharField(
    "A string", max_length=255, blank=True, default="")
```

The `null` parameter of these fields is automatically set to `False`.
