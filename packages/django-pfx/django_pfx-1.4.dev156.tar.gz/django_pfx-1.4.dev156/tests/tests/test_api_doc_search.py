from django.http import JsonResponse
from django.test import TestCase, override_settings
from django.urls import include, path

from pfx.pfxcore.decorator.rest import rest_api, rest_doc, rest_view
from pfx.pfxcore.management.commands.makeapidoc import get_spec
from pfx.pfxcore.shortcuts import register_views
from pfx.pfxcore.test import APIClient, TestAssertMixin
from pfx.pfxcore.views import (
    BaseRestView,
    ListRestViewMixin,
    ModelResponseMixin,
    parameters,
)
from tests.models import Author


@rest_view("/list/default")
class DefaultListView(ListRestViewMixin, ModelResponseMixin, BaseRestView):
    model = Author
    default_public = True


@rest_doc("", "get", search=False)
@rest_view("/list/no-search")
class NoSearchListView(ListRestViewMixin, ModelResponseMixin, BaseRestView):
    model = Author
    default_public = True


@rest_doc("", "get", search="A custom description.")
@rest_view("/list/custom-description")
class CustomDescriptionListView(
        ListRestViewMixin, ModelResponseMixin, BaseRestView):
    model = Author
    default_public = True


@rest_view("/custom")
class CustomServiceView(BaseRestView):
    model = Author
    default_public = True

    @rest_api(
        "/default", method="get", parameters=[parameters.groups.List],
        search=True)
    def get_default(self, *args, **kwargs):
        return JsonResponse({})

    @rest_api(
        "/no-search", method="get", parameters=[parameters.groups.List],
        search=False)
    def get_no_search(self, *args, **kwargs):
        return JsonResponse({})

    @rest_api(
        "/custom-description", method="get",
        parameters=[parameters.groups.List],
        search="A custom description.")
    def get_custom_description(self, *args, **kwargs):
        return JsonResponse({})


urlpatterns = [
    path('api/', include(register_views(
        DefaultListView,
        NoSearchListView,
        CustomDescriptionListView,
        CustomServiceView))),
    path('api/', include('pfx.pfxcore.urls'))
]


@override_settings(ROOT_URLCONF=__name__)
class TestAPIDocSearch(TestAssertMixin, TestCase):
    def setUp(self):
        self.client = APIClient(default_locale='en')

    def test_body_to_model(self):
        def get_params(spec, path):
            for p in self.get_val(spec, f'paths.{path}.get.parameters'):
                yield p.get('$ref') or p.get('name'), p

        spec = get_spec(set()).to_dict()

        params = dict(get_params(spec, '/list/default'))
        self.assertJEExists(params, '#/components/parameters/ListSearch')
        self.assertJENotExists(params, 'search')

        params = dict(get_params(spec, '/list/no-search'))
        self.assertJENotExists(params, '#/components/parameters/ListSearch')
        self.assertJENotExists(params, 'search')

        params = dict(get_params(spec, '/list/custom-description'))
        self.assertJENotExists(params, '#/components/parameters/ListSearch')
        self.assertJEExists(params, 'search')
        self.assertJE(params, 'search.description', "A custom description.")

        params = dict(get_params(spec, '/custom/default'))
        self.assertJEExists(params, '#/components/parameters/ListSearch')
        self.assertJENotExists(params, 'search')

        params = dict(get_params(spec, '/custom/no-search'))
        self.assertJENotExists(params, '#/components/parameters/ListSearch')
        self.assertJENotExists(params, 'search')

        params = dict(get_params(spec, '/custom/custom-description'))
        self.assertJENotExists(params, '#/components/parameters/ListSearch')
        self.assertJEExists(params, 'search')
        self.assertJE(params, 'search.description', "A custom description.")
