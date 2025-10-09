from django.urls import include, path

from pfx.pfxcore import register_views

from . import views

handler404 = 'pfx.pfxcore.views.resource_not_found'

urlpatterns = [
    path('api/', include(register_views(
        views.UserRestView))),
    path('api/', include('pfx.pfxcore.urls'))
]
