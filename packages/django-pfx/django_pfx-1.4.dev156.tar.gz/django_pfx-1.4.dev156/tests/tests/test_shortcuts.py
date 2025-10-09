from datetime import date
from decimal import Decimal as D

from django.test import TestCase

from pfx.pfxcore.exceptions import APIError, ModelNotFoundAPIError
from pfx.pfxcore.shortcuts import (
    f,
    get_bool,
    get_date,
    get_decimal,
    get_float,
    get_int,
    get_object,
    get_pk,
    parse_bool,
    parse_date,
    parse_float,
    parse_int,
)
from pfx.pfxcore.test import TestAssertMixin
from tests.models import Author, Book


class ShortcutTest(TestAssertMixin, TestCase):

    def test_f(self):
        text = f('Test {first}, {second}', first='first', second='second')
        self.assertEqual(text, 'Test first, second')

    def test_get_object(self):
        with self.assertRaises(ModelNotFoundAPIError):
            get_object(Book.objects.all(), pk=-99)
        author = Author.objects.create(
            first_name='John Ronald Reuel',
            last_name='Tolkien',
            slug='jrr-tolkien')
        a = get_object(Author.objects.all(), pk=author.pk)
        self.assertEqual(a.pk, author.pk)

    def test_get_pk(self):
        author = dict(
            pk=122,
            resource_name='John Ronald Reuel Tolkien')
        pk = get_pk(122)
        self.assertEqual(pk, 122)
        pk = get_pk(author)
        self.assertEqual(pk, 122)

    def test_parse_bool(self):
        self.assertIsNone(parse_bool(None))
        self.assertIsNone(parse_bool(''))
        self.assertIsNone(parse_bool('null'))
        self.assertIsNone(parse_bool('undefined'))
        self.assertIs(parse_bool('false'), False)
        self.assertIs(parse_bool('False'), False)
        self.assertIs(parse_bool('FALSE'), False)
        self.assertIs(parse_bool('true'), True)
        self.assertIs(parse_bool('True'), True)
        self.assertIs(parse_bool('TRUE'), True)
        with self.assertRaises(ValueError):
            parse_bool('INVALID')

    def test_get_bool(self):
        vals = dict(
            none=None,
            empty='',
            null='null',
            undefined='undefined',
            false0='false',
            false1='False',
            false2='False',
            true0='true',
            true1='True',
            true2='True',
            invalid='INVALID')
        self.assertIsNone(get_bool(vals, 'none'))
        self.assertIsNone(get_bool(vals, 'empty'))
        self.assertIsNone(get_bool(vals, 'null'))
        self.assertIsNone(get_bool(vals, 'undefined'))
        self.assertIs(get_bool(vals, 'false0'), False)
        self.assertIs(get_bool(vals, 'false1'), False)
        self.assertIs(get_bool(vals, 'false2'), False)
        self.assertIs(get_bool(vals, 'true0'), True)
        self.assertIs(get_bool(vals, 'true1'), True)
        self.assertIs(get_bool(vals, 'true2'), True)
        with self.assertRaises(APIError):
            get_bool(vals, 'invalid')
        self.assertIs(get_bool(vals, 'does_not_exists'), None)
        self.assertIs(get_bool(vals, 'does_not_exists', default=True), True)

    def test_parse_int(self):
        self.assertIsNone(parse_int(None))
        self.assertIsNone(parse_int(''))
        self.assertIsNone(parse_int('null'))
        self.assertIsNone(parse_int('undefined'))
        self.assertEqual(parse_int('0'), 0)
        self.assertEqual(parse_int('-7'), -7)
        self.assertEqual(parse_int('13'), 13)
        with self.assertRaises(ValueError):
            parse_int('INVALID')

    def test_get_int(self):
        vals = dict(
            none=None,
            empty='',
            null='null',
            undefined='undefined',
            zero='0',
            negative='-7',
            positive='13',
            invalid='INVALID')
        self.assertIsNone(get_int(vals, 'none'))
        self.assertIsNone(get_int(vals, 'empty'))
        self.assertIsNone(get_int(vals, 'null'))
        self.assertIsNone(get_int(vals, 'undefined'))
        self.assertEqual(get_int(vals, 'zero'), 0)
        self.assertEqual(get_int(vals, 'negative'), -7)
        self.assertEqual(get_int(vals, 'positive'), 13)
        with self.assertRaises(APIError):
            get_int(vals, 'invalid')
        self.assertIs(get_int(vals, 'does_not_exists'), None)
        self.assertEqual(get_int(vals, 'does_not_exists', default=42), 42)

    def test_parse_float(self):
        self.assertIsNone(parse_float(None))
        self.assertIsNone(parse_float(''))
        self.assertIsNone(parse_float('null'))
        self.assertIsNone(parse_float('undefined'))
        self.assertEqual(parse_float('0'), 0)
        self.assertEqual(parse_float('3'), 3)
        self.assertEqual(parse_float('-7.45'), -7.45)
        self.assertEqual(parse_float('13.57'), 13.57)
        with self.assertRaises(ValueError):
            parse_float('INVALID')

    def test_get_float(self):
        vals = dict(
            none=None,
            empty='',
            null='null',
            undefined='undefined',
            zero='0',
            integer='3',
            negative='-7.45',
            positive='13.57',
            invalid='INVALID')
        self.assertIsNone(get_float(vals, 'none'))
        self.assertIsNone(get_float(vals, 'empty'))
        self.assertIsNone(get_float(vals, 'null'))
        self.assertIsNone(get_float(vals, 'undefined'))
        self.assertEqual(get_float(vals, 'zero'), 0)
        self.assertEqual(get_float(vals, 'integer'), 3)
        self.assertEqual(get_float(vals, 'negative'), -7.45)
        self.assertEqual(get_float(vals, 'positive'), 13.57)
        with self.assertRaises(APIError):
            get_float(vals, 'invalid')
        self.assertIs(get_float(vals, 'does_not_exists'), None)
        self.assertEqual(get_float(
            vals, 'does_not_exists', default=3.14159265359), 3.14159265359)

    def test_get_decimal(self):
        vals = dict(
            none=None,
            empty='',
            null='null',
            undefined='undefined',
            zero='0',
            integer='3',
            negative='-7.45',
            positive='13.57',
            invalid='INVALID')
        self.assertIsNone(get_decimal(vals, 'none'))
        self.assertIsNone(get_decimal(vals, 'empty'))
        self.assertIsNone(get_decimal(vals, 'null'))
        self.assertIsNone(get_decimal(vals, 'undefined'))
        self.assertEqual(get_decimal(vals, 'zero'), D('0'))
        self.assertEqual(get_decimal(vals, 'integer'), D('3'))
        self.assertEqual(get_decimal(vals, 'negative'), D('-7.45'))
        self.assertEqual(get_decimal(vals, 'positive'), D('13.57'))
        with self.assertRaises(APIError):
            get_decimal(vals, 'invalid')
        self.assertIs(get_decimal(vals, 'does_not_exists'), None)
        self.assertEqual(get_decimal(
            vals, 'does_not_exists',
            default=D('3.14159265359')), D('3.14159265359'))

    def test_parse_date(self):
        self.assertIsNone(parse_date(None))
        self.assertIsNone(parse_date(''))
        self.assertIsNone(parse_date('null'))
        self.assertIsNone(parse_date('undefined'))
        self.assertEqual(parse_date('2020-05-17'), date(2020, 5, 17))
        with self.assertRaises(ValueError):
            parse_date('INVALID')

    def test_get_date(self):
        vals = dict(
            none=None,
            empty='',
            null='null',
            undefined='undefined',
            date='2020-05-17',
            invalid='INVALID')
        self.assertIsNone(get_date(vals, 'none'))
        self.assertIsNone(get_date(vals, 'empty'))
        self.assertIsNone(get_date(vals, 'null'))
        self.assertIsNone(get_date(vals, 'undefined'))
        self.assertEqual(get_date(vals, 'date'), date(2020, 5, 17))
        with self.assertRaises(APIError):
            get_date(vals, 'invalid')
        self.assertIs(get_date(vals, 'does_not_exists'), None)
        self.assertEqual(get_date(
            vals, 'does_not_exists', default=date(2020, 5, 21)
        ), date(2020, 5, 21))
