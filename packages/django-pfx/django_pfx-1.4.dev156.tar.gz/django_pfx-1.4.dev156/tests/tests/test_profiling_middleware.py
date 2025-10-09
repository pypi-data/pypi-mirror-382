import logging
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

from pfx.pfxcore.middleware import profiling
from pfx.pfxcore.test import APIClient, TestAssertMixin

logger = logging.getLogger(__name__)


@override_settings(
    DEBUG=True,
    MIDDLEWARE=[
        'pfx.pfxcore.middleware.ProfilingMiddleware'
    ] + settings.MIDDLEWARE)
class ProfilingMiddlewareTest(TestAssertMixin, TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch.object(profiling.logger, 'debug')
    def test_profile(self, mock_debug):
        response = self.client.get('/api/authors?items=1&count=1')
        self.assertRC(response, 200)
        self.assertTrue(mock_debug.called)
        log = mock_debug.call_args[0][0]
        self.assertIn('GET /api/authors?items=1&count=1 200', log)
        self.assertIn('SQL queries: 2', log)
        self.assertNotIn('SELECT COUNT(*)', log)
        self.assertNotIn('SELECT DISTINCT', log)
        self.assertNotIn('Ordered by: cumulative time', log)
        self.assertNotIn('ncalls  tottime  percall  cumtime  percall', log)

    @override_settings(
        PFX_PROFILING_SQL='/api/authors')
    @patch.object(profiling.logger, 'debug')
    def test_profile_sql(self, mock_debug):
        response = self.client.get('/api/authors?items=1&count=1')
        self.assertRC(response, 200)
        self.assertTrue(mock_debug.called)
        log = mock_debug.call_args[0][0]
        self.assertIn('GET /api/authors?items=1&count=1 200', log)
        self.assertIn('SQL queries: 2', log)
        self.assertIn('SELECT COUNT(*)', log)
        self.assertIn('SELECT DISTINCT', log)

    @override_settings(
        PFX_PROFILING_SQL='/api/books')
    @patch.object(profiling.logger, 'debug')
    def test_profile_sql_other_path(self, mock_debug):
        response = self.client.get('/api/authors?items=1&count=1')
        self.assertRC(response, 200)
        self.assertTrue(mock_debug.called)
        log = mock_debug.call_args[0][0]
        self.assertIn('GET /api/authors?items=1&count=1 200', log)
        self.assertIn('SQL queries: 2', log)
        self.assertNotIn('SELECT COUNT(*)', log)
        self.assertNotIn('SELECT DISTINCT', log)

    @override_settings(
        PFX_PROFILING_CPROFILE='/api/authors')
    @patch.object(profiling.logger, 'debug')
    def test_profile_cprofile(self, mock_debug):
        response = self.client.get('/api/authors?items=1&count=1')
        self.assertRC(response, 200)
        self.assertTrue(mock_debug.called)
        log = mock_debug.call_args[0][0]
        # print(log)
        self.assertIn('GET /api/authors?items=1&count=1 200', log)
        self.assertIn('SQL queries: 2', log)
        self.assertIn('Ordered by: cumulative time', log)
        self.assertIn('ncalls  tottime  percall  cumtime  percall', log)

    @override_settings(
        PFX_PROFILING_CPROFILE='/api/books')
    @patch.object(profiling.logger, 'debug')
    def test_profile_cprofile_other_path(self, mock_debug):
        response = self.client.get('/api/authors?items=1&count=1')
        self.assertRC(response, 200)
        self.assertTrue(mock_debug.called)
        log = mock_debug.call_args[0][0]
        self.assertIn('GET /api/authors?items=1&count=1 200', log)
        self.assertIn('SQL queries: 2', log)
        self.assertNotIn('Ordered by: cumulative time', log)
        self.assertNotIn('ncalls  tottime  percall  cumtime  percall', log)
