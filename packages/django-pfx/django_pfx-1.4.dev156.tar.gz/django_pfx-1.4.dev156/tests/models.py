from django.core.mail import send_mail
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from pfx.pfxcore.decorator import rest_property
from pfx.pfxcore.fields import MediaField, MinutesDurationField
from pfx.pfxcore.models import (
    AbstractPFXUser,
    CacheableMixin,
    CacheDependsMixin,
    JSONReprMixin,
    NotNullCharField,
    NotNullURLField,
    OtpUserMixin,
    PFXModelMixin,
    UniqueConstraint,
    UserFilteredQuerySetMixin,
)
from pfx.pfxcore.storage import LocalStorage


class User(CacheableMixin, OtpUserMixin, AbstractPFXUser):
    """Default user for tests."""

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class AuthorQuerySet(models.QuerySet):
    def default_search(self, search):
        return (
            Q(first_name__unaccent__icontains=search) |
            Q(last_name__unaccent__icontains=search))


class BadUserAuthorQuerySet(UserFilteredQuerySetMixin, models.QuerySet):
    pass


class UserAuthorQuerySet(UserFilteredQuerySetMixin, models.QuerySet):
    def user(self, user):
        if not user.is_superuser:
            return self.exclude(last_name="Tolkien")
        return self


class Author(CacheableMixin, JSONReprMixin, models.Model):
    CACHED_PROPERTIES = ['books_count']
    api = '/authors'

    first_name = models.CharField(_("First Name"), max_length=30)
    last_name = models.CharField(_("Last Name"), max_length=30)
    slug = models.SlugField("Slug", unique=True)
    gender = models.CharField("Gender", max_length=10, choices=[
        ('male', "Male"), ('female', "Female")], default='male')
    science_fiction = models.BooleanField("Science Fiction", default=False)
    created_at = models.DateField("Created at", auto_now_add=True)
    create_comment = NotNullCharField(
        "Create comment", max_length=255, blank=True)
    update_comment = NotNullCharField(
        "Update comment", max_length=255, blank=True)
    website = NotNullURLField("Website", max_length=255, blank=True)
    types = models.ManyToManyField(
        'tests.BookType', related_name='authors',
        verbose_name="Types")

    objects = AuthorQuerySet.as_manager()
    bad_user_objects = BadUserAuthorQuerySet.as_manager()
    user_objects = UserAuthorQuerySet.as_manager()

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"
        ordering = ['last_name', 'first_name', 'pk']
        permissions = [("can_customize_author", "Can customize author")]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @rest_property("Name Length", "IntegerField")
    def name_length(self):
        return len(str(self))

    @cached_property
    def books_count(self):
        return self.books.count()

    @property
    def books_count_prop(self):
        return self.books.count()

    def json_repr(self, **values):
        """JSON representation.
        ---
        new_field:
            type: string
        """
        return super().json_repr(new_field="A value", **values)


class BookType(CacheDependsMixin, PFXModelMixin, models.Model):
    CACHE_DEPENDS_FIELDS = ['books.author']

    name = models.CharField("Name", max_length=30)
    slug = models.SlugField("Slug")

    class Meta:
        verbose_name = "Book Type"
        verbose_name_plural = "Book Types"

    def __str__(self):
        return f"{self.name}"


class Book(CacheDependsMixin, PFXModelMixin, models.Model):
    CACHE_DEPENDS_FIELDS = ['author']

    name = models.CharField("Name", max_length=100)
    author = models.ForeignKey(
        'tests.Author', on_delete=models.RESTRICT,
        related_name='books', verbose_name="Author")
    type = models.ForeignKey(
        'tests.BookType', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='books', verbose_name="Book Type")
    pub_date = models.DateField("Pub Date")
    created_at = models.DateField("Created at", auto_now_add=True)
    pages = models.IntegerField("Pages", null=True, blank=True)
    rating = models.FloatField("Rating", null=True, blank=True)
    reference = models.CharField(
        "Reference", max_length=30, null=True, blank=True)
    cover = MediaField(
        "Cover", auto_delete=True, blank=True, null=True)
    local_file = MediaField(
        "Cover", auto_delete=True, blank=True, null=True,
        storage=LocalStorage())
    read_time = MinutesDurationField("Read Time", null=True, blank=True)

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        constraints = [
            UniqueConstraint(
                fields=['author', 'name'],
                name='book_unique_author_and_name',
                message="%(name)s already exists for %(author)s")]

    def __str__(self):
        return f"{self.name}"

    def json_repr(self, **values):
        """JSON representation.
        ---
        author_name:
            type: string
        """
        return super().json_repr(author_name=str(self.author), **values)
