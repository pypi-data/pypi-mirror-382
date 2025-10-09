
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from pfx.pfxcore.exceptions import APIError
from pfx.pfxcore.models import OrderedModelMixin
from pfx.pfxcore.shortcuts import f

from .rest_views import ModelResponseMixin


class OrderedRestViewMixin(ModelResponseMixin):
    """Extension mixin for OrderedModelMixin models."""

    def __init__(self, *args, **kwargs):
        if not issubclass(self.model, OrderedModelMixin):
            raise TypeError("model is not a subclass of OrderedModelMixin")
        super().__init__(*args, **kwargs)

    def is_valid(self, obj, created=False, **kwargs):
        with transaction.atomic():
            res = super().is_valid(obj, created, **kwargs)
            self.apply_move(obj)
        return res

    def apply_move(self, obj):
        def get_object(move):
            pk = self.request.GET.get('object')
            if not pk:
                raise APIError(f(
                    _("object parameter is mandatory for move={move}."),
                    move=move))
            try:
                return self.get_queryset(
                    from_queryset=obj._order_qs).get(pk=pk)
            except ObjectDoesNotExist:
                raise APIError(f(
                    _("object {pk} does not exists in this move context."),
                    pk=pk))

        move = self.request.GET.get('move')
        if move == 'up':
            obj.up()
        elif move == 'down':
            obj.down()
        elif move == 'bottom':
            obj.bottom()
        elif move == 'top':
            obj.top()
        elif move == 'above':
            obj.above(get_object(move))
        elif move == 'below':
            obj.below(get_object(move))
