from django.urls import include, path

from pfx.pfxcore import register_views

from . import views

handler404 = 'pfx.pfxcore.views.resource_not_found'

urlpatterns = [
    path('api/', include(register_views(
        views.AuthorRestView,
        views.AuthorExtraMetaRestView,
        views.AuthorAnnotateRestView,
        views.AuthorFieldsPropsRestView,
        views.PrivateEditAuthorRestView,
        views.PrivateAuthorRestView,
        views.PermsAuthorRestView,
        views.AdminEditAuthorRestView,
        views.AdminAuthorRestView,
        views.BookRestView,
        views.BookCustomAuthorRestView,
        views.PermsBookRestView,
        views.BookTypeRestView,
        views.Testi18nView,
        views.TestErrorView,
        views.TestTimezoneView))),
    path('api/does-not-exists', views.AuthorRestView.as_view(
        pfx_methods=dict(get='does_not_exists'))),
    path('api/', include('pfx.pfxcore.urls'))
]
