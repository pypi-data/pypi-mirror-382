import logging
import re
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class MinutesDurationField(models.DurationField):
    RE_FLOAT = re.compile(r'^[0-9]*(\.[0-9]*)?$')
    RE_HH_MM = re.compile(r'^([0-9]*):([0-5][0-9])?$')
    RE_HUMAN = re.compile(
        r'^\s*(?:([0-9]*(?:\.[0-9]*)?)h)?\s*(?:([0-9]*)m)?\s*$')
    schema = dict(type='object', properties=dict(
        minutes=dict(type='number', example=90),
        clock_format=dict(type='string', example='01:30'),
        human_format=dict(type='string', example='1h 30m')))

    def to_python(self, value):
        if value is None or value == '':
            return None
        if isinstance(value, timedelta):
            return value
        if isinstance(value, (int, float)):
            return timedelta(hours=value)
        if not isinstance(value, str):
            logger.error(f"invalid value {value} [{type(value)}]")
            raise ValidationError(_("Invalid value."))
        match_float = self.RE_FLOAT.match(value)
        if match_float:
            return timedelta(hours=float(value))
        match_hm = self.RE_HH_MM.match(value)
        if match_hm:
            h, m = match_hm.groups()
            return timedelta(
                hours=h and int(h) or 0, minutes=m and int(m) or 0)
        match_human = self.RE_HUMAN.match(value)
        if match_human:
            h, m = match_human.groups()
            return timedelta(
                hours=h and float(h) or 0, minutes=m and int(m) or 0)
        raise ValidationError(_(
            "Invalid format, it can be a number in hours, “1:05”, “:05”, "
            "“1h 5m”, “1.5h” or “30m”."))

    @staticmethod
    def to_json(value):
        if value is None:
            return None
        minutes = int(value.total_seconds() / 60)
        h, m = minutes // 60, minutes % 60
        return dict(
            minutes=minutes,
            clock_format=f"{minutes // 60}:{minutes % 60:02d}",
            human_format=(
                f'{h and f"{h}h" or ""}\u00A0'
                f'{m and f"{m}m" or ""}'.strip()))
