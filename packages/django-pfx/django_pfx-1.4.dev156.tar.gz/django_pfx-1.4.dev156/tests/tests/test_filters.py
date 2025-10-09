from django.db.models import Q
from django.test import TestCase

from pfx.pfxcore.test import TestAssertMixin
from pfx.pfxcore.views import Filter


class MockParams:
    def __init__(self, **params):
        self.params = params

    def getlist(self, key):
        return self.params.get(key) or []


class FiltersTest(TestAssertMixin, TestCase):
    def test_filter_func(self):
        filter = Filter('test', "Test", filter_func=lambda v: Q(test=v))
        q = filter.query(MockParams(test=["A test value"]))
        self.assertEqual(str(q), "(AND: ('test', 'A test value'))")

    def test_filter_func_defaults(self):
        filter = Filter(
            'test', "Test", filter_func=lambda v: Q(test=v),
            defaults=["A default value"])
        q = filter.query(MockParams(test=[]))
        self.assertEqual(str(q), "(AND: ('test', 'A default value'))")
        q = filter.query(MockParams(test=["A test value"]))
        self.assertEqual(str(q), "(AND: ('test', 'A test value'))")

    def test_filter_func_multi(self):
        filter = Filter('test', "Test", filter_func=lambda v: Q(test=v))
        q = filter.query(MockParams(test=["A test value", "another"]))
        self.assertEqual(
            str(q), "(OR: ('test', 'A test value'), ('test', 'another'))")

    def test_filter_func_multi_and(self):
        filter = Filter(
            'test', "Test", filter_func=lambda v: Q(test=v),
            filter_func_and=True)
        q = filter.query(MockParams(test=["A test value", "another"]))
        self.assertEqual(
            str(q), "(AND: ('test', 'A test value'), ('test', 'another'))")

    def test_filter_func_multi_list(self):
        filter = Filter(
            'test', "Test", filter_func=lambda v: Q(test=v),
            filter_func_list=True)
        q = filter.query(MockParams(test=["A test value", "another"]))
        self.assertEqual(
            str(q), "(AND: ('test', ['A test value', 'another']))")
