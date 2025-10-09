from decimal import Decimal

from django.db import models


class DecimalField(models.DecimalField):
    def __init__(
            self, *args, percent=False, currency=None,
            json_decimal_places=None, **kw):
        super().__init__(*args, **kw)
        self.percent = percent
        self.currency = currency
        self.json_quantize = Decimal(10) ** -(json_decimal_places or (
            percent and self.decimal_places - 2 or self.decimal_places))

    def to_json_meta(self, meta):
        meta.update(
            percent=self.percent,
            currency=self.currency)
        return meta

    def to_json(self, value):
        if value is None:
            return None
        if self.percent:
            value *= Decimal(100)
        return value.quantize(self.json_quantize)

    def from_json(self, value):
        if value is None or value == '':
            return None
        try:
            value = Decimal(value)
        except Exception:
            return value
        return self.percent and value / Decimal('100') or value
