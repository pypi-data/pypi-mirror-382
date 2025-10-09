import logging

from django.core.exceptions import FieldDoesNotExist
from django.http import FileResponse, HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from pfx.pfxcore.decorator import rest_api
from pfx.pfxcore.exceptions import APIError, NotFoundError
from pfx.pfxcore.fields import MediaField
from pfx.pfxcore.http import JsonResponse
from pfx.pfxcore.shortcuts import get_bool, settings
from pfx.pfxcore.storage.s3_storage import StorageException

from . import parameters
from .rest_views import ModelMixin

logger = logging.getLogger(__name__)


def get_medial_field(model, field):
    try:
        model_field = model._meta.get_field(field)
        if not isinstance(model_field, MediaField):
            raise NotFoundError  # pragma: no cover
    except FieldDoesNotExist:  # pragma: no cover
        raise NotFoundError
    return model_field


def get_media_field_response(obj, field, request):
    mediaField = get_medial_field(obj, field)
    try:
        url = mediaField.get_url(request, obj)
    except StorageException as e:  # pragma: no cover
        logger.exception(e)
        raise APIError(_("Unexpected storage error", status=500))

    if mediaField.storage.direct:
        attr = getattr(obj, field)
        filename = attr.get('name')
        if settings.STORAGE_LOCAL_X_ACCEL_REDIRECT:
            response = HttpResponse()
            response["Content-Disposition"] = (
                f"attachment; filename={filename}")
            response["Content-Type"] = attr.get('content-type', '')
            response['X-Accel-Redirect'] = (
                f"/filestore/{attr.get('key')}")
            return response
        response = FileResponse(
            open(url, 'rb'),
            as_attachment=True, filename=attr.get('name'))
        return response

    if get_bool(request.GET, 'redirect'):
        return redirect(url)
    return JsonResponse(dict(url=url))


class MediaRestViewMixin(ModelMixin):
    """Extension mixin to manage media fields."""

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.media_fields = set()
        for field in self.model._meta.fields:
            if isinstance(field, MediaField):
                self.media_fields.add(field)

    @rest_api(
        "/<int:pk>/<str:field>/upload-url/<str:filename>", method="get",
        priority_doc=-8)
    def field_media_upload_url(self, pk, field, filename, *args, **kwargs):
        """Entrypoint for
        :code:`GET /<int:pk>/<str:field>/upload-url/<str:filename>` route.

        Get the upload URL for a media file.

        :param pk: The object pk
        :param field: The field name
        :param filename: The file name
        :returns: The JSON response
        :rtype: :class:`JsonResponse`
        ---
        get:
            summary: Get upload URL
            description: |
                Get upload URL for a `MediaField` field.

                You can upload a file ont the received URL. When the upload
                query is done, you have to confirm the process with an
                update request (`PUT`) on {model}. The body of this request
                must contain the name of the `MediaField` with the contents
                of the `file` value in the response of this request.

                1. `GET /<int:pk>/<str:field>/upload-url/<str:filename>`
                    → `data`
                2. `PUT data.url aFile Content-Type: aFile.type`
                3. `PUT /<int:pk> {{field: data.file}}`
            parameters extras:
                pk: The {model} pk.
                field: The {model} field name. Must be the name of
                    a `MediaField` field.
                filename: The desired filename.
            responses:
                200:
                    description: The upload URL
                    content:
                        application/json:
                            schema:
                                properties:
                                    url:
                                        type: string
                                        format: uri
                                    file:
                                        type: object
                                        properties:
                                            name:
                                                type: string
                                            key:
                                                type: string
        """
        obj = self.get_object(pk=pk)
        mediaField = get_medial_field(self.model, field)
        if mediaField.storage.direct:
            raise APIError("Unavailable for direct storage")
        try:
            res = mediaField.get_upload_url(self.request, obj, filename)
        except StorageException as e:  # pragma: no cover
            logger.exception(e)
            raise APIError(_("Unexpected storage error", status=500))
        return JsonResponse(res)

    @rest_api(
        "/<int:pk>/<str:field>", method="get",
        parameters=[parameters.MediaRedirect], priority_doc=-9)
    def field_media_get(self, pk, field, *args, **kwargs):
        """Entrypoint for :code:`GET /<int:pk>/<str:field>` route.

        Get the download URL for a media file.

        :param pk: The object pk
        :param field: The field name
        :returns: The JSON response
        :rtype: :class:`JsonResponse`
        ---
        get:
            summary: Get {model} file
            description: Get the URL for a media field file.
            parameters extras:
                pk: the {model} pk
                field: the {model} field name
            responses:
                200:
                    description: |
                        The file stream if storage is direct,
                        otherwise the file URL, only if `redirect` is `false`.
                    content:
                        application/json:
                            schema:
                                properties:
                                    url:
                                        type: string
                                        format: uri
                        application/octet-stream:
                            schema:
                                type: file
                302:
                    description: |
                        The redirect, for undirect storage
                        if `redirect` is `true`.
        """
        obj = self.get_object(pk=pk)
        return get_media_field_response(obj, field, self.request)

    def pre_save(self, obj, created=False):
        funcs = super().pre_save(obj, created=created)
        for field in self.media_fields:
            funcs.extend(field.media_pre_save(obj))
        return funcs


class MediaPermsRestViewMixin(MediaRestViewMixin):
    """Extension mixin to check permissions."""

    def field_media_upload_url_perm(self, *args, **kwargs):
        return self.request.user.has_perm(*self.get_model_perms('change'))

    def field_media_get_perm(self, *args, **kwargs):
        return self.request.user.has_perm(*self.get_model_perms('view'))
