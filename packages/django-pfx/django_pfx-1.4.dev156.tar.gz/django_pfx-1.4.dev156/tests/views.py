import logging

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Count, Q, Value
from django.db.models.functions import Coalesce
from django.utils.translation import gettext as _

from pfx.pfxcore.decorator import rest_api, rest_doc, rest_view
from pfx.pfxcore.http import JsonResponse
from pfx.pfxcore.views import (
    VF,
    BaseRestView,
    FieldType,
    Filter,
    FilterGroup,
    MediaPermsRestViewMixin,
    MediaRestViewMixin,
    ModelFilter,
    PermsRestView,
    RestView,
    SlugDetailRestViewMixin,
    SlugPermsDetailRestViewMixin,
)

from .models import Author, Book, BookType

logger = logging.getLogger(__name__)


class AuthorRestViewMixin():
    model = Author
    fields = [
        'first_name', 'last_name', 'name_length', 'slug', 'gender', 'types',
        VF('books', readonly=True), VF('created_at', readonly=True),
        VF('create_comment', readonly_update=True),
        VF('update_comment', readonly_create=True), 'website']
    list_fields = ['first_name', 'last_name', 'gender']


def heroic_fantasy_filter(value):
    q = Q(last_name="Tolkien")
    return value and q or ~q


def last_name_filter(value):
    return Q(last_name__isnull=not value)


def last_name_choices_filter(value):
    return Q(last_name=value)


def pub_date_gte_filter(value):
    return Q(pub_date__gte=value)


def author_pk_filter(value):
    return Q(author__pk=value)


@rest_view("/authors")
class AuthorRestView(AuthorRestViewMixin, SlugDetailRestViewMixin, RestView):
    default_public = True
    filters = [
        FilterGroup('book_type', _("Book Type"), [
            ModelFilter(Author, 'science_fiction', technical=True),
            Filter(
                'heroic_fantasy', _("Heroic Fantasy"),
                FieldType.BooleanField, heroic_fantasy_filter),
            ModelFilter(Author, 'types', related_model_api='/book-types')
        ]),
        FilterGroup('custom', _("Custom"), [
            ModelFilter(
                Author, 'last_name', type=FieldType.BooleanField,
                filter_func=last_name_filter),
            ModelFilter(Author, 'first_name'),
            ModelFilter(Author, 'gender'),
            Filter(
                'last_name_choices', _("Tolkien or Asimov"),
                FieldType.CharField, last_name_choices_filter,
                choices=[('Tolkien', "Tolkien"), ('Asimov', "Asimov")],
                empty_value=False),
        ]),
    ]

    @rest_api("/cache/<int:id>", method="get", groups=['cache'])
    def cache_get(self, id, *args, **kwargs):
        book = Author.cache_get(id)
        if book:
            return self.response(book, from_cache=True)
        book = self.get_object(pk=id)
        book.cache()
        return self.response(book, from_cache=False)

    @rest_api("/priority/default", method="get")
    def priority_default(self, *args, **kwargs):
        return JsonResponse(dict(value='static:default'))

    @rest_api("/priority/<value>", method="get")
    def priority_param(self, value, *args, **kwargs):
        return JsonResponse(dict(value=f"untyped:{value}"))

    @rest_api("/priority/<int:value>", method="get")
    def priority_int(self, value, *args, **kwargs):
        return JsonResponse(dict(value=f"int:{value}"))

    @rest_api("/priority/<str:value>", method="get")
    def priority_str(self, value, *args, **kwargs):
        return JsonResponse(dict(value=f"str:{value}"))

    @rest_api("/priority/<path:value>", method="get")
    def priority_path(self, value, *args, **kwargs):
        return JsonResponse(dict(value=f"path:{value}"))

    @rest_api("/priority/default/path", method="get")
    def priority_default_path(self, *args, **kwargs):
        return JsonResponse(dict(value="static:default_path"))

    @rest_api("/priority/priority-less", method="get", priority=-1)
    def priority_test2(self, *args, **kwargs):
        return JsonResponse(dict(value='static:less'))

    @rest_api("/priority/priority-more", method="get", priority=1)
    def priority_test3(self, *args, **kwargs):
        return JsonResponse(dict(value='static:more'))


@rest_view("/authors-extra-meta")
class AuthorExtraMetaRestView(AuthorRestViewMixin, RestView):
    default_public = True

    def _get_list_extra_meta(self, res):
        return dict(test="Hello world")


def books_json_repr(book):
    """JSON representation.
    ---
    _extends: true
    author_gender:
        type: string
    """
    return book.json_repr(author_gender=book.author.gender)


@rest_doc('/<int:id>', 'get', summary="Get custom author", groups=["custom"])
@rest_view("/authors-annotate")
class AuthorAnnotateRestView(AuthorRestView):
    fields = [
        'first_name', 'last_name', 'slug',
        VF('books', json_repr=books_json_repr),
        'books_count', 'books_count_annotate', 'books_count_prop']
    list_fields = [
        'first_name', 'last_name', 'slug',
        'books_count', 'books_count_annotate', 'books_count_prop']

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).annotate(
            books_count_annotate=Count('books'))


@rest_view("/authors-fields-props")
class AuthorFieldsPropsRestView(AuthorRestView):
    fields = [
        'first_name', 'last_name', 'slug',
        VF('books_count', "Books Count", "IntegerField"),
        VF('books_count_annotate', "Books Count (annotate)", "IntegerField"),
        VF('books_count_prop', "Books Count (property)", "IntegerField")]
    list_fields = [
        'first_name', 'last_name', 'slug',
        VF('books_count', "B.C.", "IntegerField"),
        VF('books_count_annotate', "B.C. (a)", "IntegerField"),
        VF('books_count_prop', "B.C. (p)", "IntegerField")]

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).annotate(
            books_count_annotate=Count('books'))


@rest_view("/private-edit/authors")
class PrivateEditAuthorRestView(AuthorRestViewMixin, RestView):
    get_public = True
    get_list_public = True


@rest_view("/private/authors")
class PrivateAuthorRestView(AuthorRestViewMixin, RestView):
    pass


@rest_view("/perms/authors")
class PermsAuthorRestView(
        AuthorRestViewMixin, SlugPermsDetailRestViewMixin, PermsRestView):

    @rest_api("/custom", method="get", perms='tests.view_author')
    def get_custom(self):
        return JsonResponse(dict(message='Custom get'))

    @rest_api("/custom", method="put", perms=[
        'tests.change_author', 'tests.can_customize_author'])
    def get_custom_action(self):
        return JsonResponse(dict(message='Custom put'))


@rest_view("/admin-edit/authors")
class AdminEditAuthorRestView(AuthorRestViewMixin, RestView):
    def put_perm(self, id, *args, **kwargs):
        return self.request.user.is_superuser


@rest_view("/admin/authors")
class AdminAuthorRestView(AuthorRestViewMixin, RestView):
    def perm(self):
        return self.request.user.is_superuser


class BookRestViewMixin():
    model = Book
    fields = [
        'name', 'author', 'pub_date', VF('created_at', readonly=True),
        'type', 'cover', 'local_file', 'pages', 'rating', 'author__last_name',
        'read_time']
    filters = [
        FilterGroup('custom', _("Custom"), [
            ModelFilter(Book, 'author'),
            ModelFilter(Book, 'type'),
            ModelFilter(Book, 'pages'),
            ModelFilter(Book, 'rating'),
            ModelFilter(Book, 'pub_date'),
            Filter(
                'pub_date_gte', _("Publication Date greater than"),
                FieldType.DateField, pub_date_gte_filter),
            Filter(
                'author_pk', _("Author PK"),
                FieldType.ModelObject, author_pk_filter,
                related_model=Author),
        ]),
    ]


@rest_view("/books")
class BookRestView(BookRestViewMixin, MediaRestViewMixin, RestView):
    default_public = True

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).annotate(
            pages_null=Coalesce('pages', Value(0)))

    def get_order_mapping(self, *order):
        return dict(pages='pages_null')


@rest_view("/perms/books")
class PermsBookRestView(
        BookRestViewMixin, MediaPermsRestViewMixin, PermsRestView):
    pass


def author_json_repr(obj):
    """JSON representation.
    ---
    hello:
        type: string
    last_name:
        type: string
    """
    return obj.json_repr(
        hello="World",
        last_name=obj.last_name)


@rest_view("/books-custom-author")
class BookCustomAuthorRestView(BookRestView):
    fields = [
        VF('name', alias='book_name'),
        VF('author', json_repr=author_json_repr),
        VF('author__last_name', alias='author_last_name'),
        'pub_date']


@rest_view("/book-types")
class BookTypeRestView(RestView):
    model = BookType
    fields = ['name', 'slug']
    default_public = True


@rest_view("/test-i18n")
class Testi18nView(BaseRestView):
    default_public = True

    @rest_api("", method="get")
    def get(self, *args, **kwargs):
        return JsonResponse({'Monday': _("Monday")})


@rest_view("/error")
class TestErrorView(BaseRestView):
    default_public = True

    @rest_api("/500", method="get")
    def raise_500(self):
        raise ImproperlyConfigured("Test exception")


@rest_view("/timezone")
class TestTimezoneView(BaseRestView):
    default_public = True

    @rest_api("", method="get")
    def get(self):
        return JsonResponse({'tz': self.request.TIMEZONE})


@rest_view("/illegal-priority")
class IllegalPriorityRestView(BaseRestView):
    default_public = True

    @rest_api("/test", method="get", priority=1)
    def get(self, *args, **kwargs):
        return JsonResponse(dict(value='test'))

    @rest_api("/test", method="put", priority=2)
    def put(self, *args, **kwargs):
        return JsonResponse(dict(value='test'))


class FakeViewMixin:
    """This mixin allow to create a test view that is not processsed
    by makeapidoc."""

    @classmethod
    def as_urlpatterns(cls):
        return cls.get_urls(as_pattern=True)
