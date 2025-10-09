import logging

from django.test import TestCase
from django.test.utils import override_settings

from pfx.pfxcore.test import APIClient, TestAssertMixin

logger = logging.getLogger(__name__)


class TimezoneMiddlewareTest(TestAssertMixin, TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_django_default_tz(self):
        response = self.client.get('/api/timezone')
        self.assertJE(response, "tz", 'America/Chicago')

    @override_settings(TIME_ZONE="Asia/Tokyo")
    def test_settings_default_tz(self):
        response = self.client.get('/api/timezone')
        self.assertJE(response, "tz", 'Asia/Tokyo')

    @override_settings(TIME_ZONE="Asia/Tokyo")
    def test_header_tz(self):
        response = self.client.get(
            '/api/timezone',  HTTP_X_CUSTOM_TIMEZONE="Europe/Zurich")
        self.assertJE(response, "tz", 'Europe/Zurich')

    @override_settings(TIME_ZONE="Asia/Tokyo")
    def test_header_unknown_tz(self):
        response = self.client.get(
            '/api/timezone',  HTTP_X_CUSTOM_TIMEZONE="Europe/Unknown")
        self.assertJE(response, "tz", 'Asia/Tokyo')
