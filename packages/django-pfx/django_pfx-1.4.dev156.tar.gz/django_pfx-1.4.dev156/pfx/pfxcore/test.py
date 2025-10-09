import json
import logging
import re
from functools import reduce
from http.cookies import SimpleCookie
from json import JSONDecodeError

from django.db import transaction
from django.test.client import Client as DjangoClient

logger = logging.getLogger(__name__)


def format_response(r, title="http response"):
    res = []
    res.append(f"\n******************** {title} ********************")
    if not r:
        res.append("Response is null")
    res.append(f"Status: {r.status_code} {r.reason_phrase}")
    res.append("Headers: ")
    res.append("\n".join(f"  {k}: {v}" for k, v in r.headers.items()))
    res.append("Content: ")
    if hasattr(r, 'json_content'):
        res.append(json.dumps(r.json_content, indent=4, sort_keys=True))
    elif hasattr(r, 'content') and r.content:
        res.append(str(r.content))
    elif hasattr(r, 'streaming_content'):
        res.append("Streaming content")
    else:
        res.append("Response is empty")
    res.append("*******************************************************")
    return '\n'.join(res)


def format_request(r, title="http request"):
    res = []
    res.append(f"\n******************** {title} ********************")
    if not r:
        return "Request is null"
    res.append(f"Path: {r.path_info}")
    res.append(f"Method: {r.method}")
    res.append("Query params:")
    res.append("\n".join(f"  {k}: {v}" for k, v in r.GET.items()))
    res.append("Headers: ")
    res.append("\n".join(f"  {k}: {v}" for k, v in r.headers.items()))
    res.append("Content: ")
    if r.content_type == 'application/json':
        try:
            res.append(
                json.dumps(json.loads(r.body), indent=4, sort_keys=True))
        except JSONDecodeError:
            res.append("Json Decode Error")
            res.append(str(r.body))
    elif r.body:
        res.append(str(r.body))
    else:
        res.append("Request is empty")
    res.append("*******************************************************")
    return '\n'.join(res)


def get_auth_cookie(response):
    return [
        v for k, v in response.client.cookies.items()
        if k == 'token'][0]


def get_url(path, **params):
    if params:
        param_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{path}?{param_string}"
    return path


class APIClient(DjangoClient):

    token = None
    default_locale = None
    auth_cookie = None

    def __init__(self, enforce_csrf_checks=False, raise_request_exception=True,
                 default_locale=None, with_cookie=False, **defaults):
        super().__init__(enforce_csrf_checks, raise_request_exception,
                         **defaults)
        self.default_locale = default_locale
        self.with_cookie = with_cookie

    def login(self, username, password='test',
              path='/api/auth/login', locale=None, remember_me=False):
        self.token = None
        response = self.post(
            get_url(path, mode=(self.with_cookie and 'cookie' or 'jwt')),
            dict(
                username=username,
                password=password,
                remember_me=remember_me),
            locale=locale)
        if response.status_code == 200:
            if self.with_cookie:
                self.auth_cookie = get_auth_cookie(response)
                regex = r".*token=([\w\._-]*);.*"
                self.token = re.findall(regex, str(self.auth_cookie))[0]
            else:
                self.token = response.json_content['token']
            return True
        return False

    def logout(self):
        self.token = None

    def generic(self, method, path, data='',
                content_type='application/octet-stream', secure=False,
                locale=None, print_request=False, **extra):
        cookies = extra.pop('cookies', {})
        if self.token:
            if self.with_cookie:
                cookies['token'] = self.token
            else:
                extra.update(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        if cookies:
            if self.cookies:
                for k, v in cookies.items():
                    self.cookies[k] = v
            else:
                self.cookies = SimpleCookie(cookies)
        if locale:
            extra.update(HTTP_X_CUSTOM_LANGUAGE=f"{locale}")
        elif self.default_locale:
            extra.update(HTTP_X_CUSTOM_LANGUAGE=f"{self.default_locale}")
        if print_request:
            extra.update(HTTP_X_PRINT_REQUEST="true")
        return super().generic(
            method, path, data, content_type, secure, **extra)

    @staticmethod
    def decode_response(response, method):
        if (response.headers['Content-Type'] == 'application/json'
                and method not in ['head', 'option', 'trace']):
            response.json_content = response.json()
        response.formatted = lambda: format_response(response)
        response.print = lambda: print(format_response(response))
        return response

    def get(self, path, data=None, secure=False, locale=None, **extra):
        return self.decode_response(
            super().get(
                path, data=data, secure=secure, locale=locale, **extra),
            method='get')

    def post(self, path, data=None, content_type='application/json',
             secure=False, locale=None, **extra):
        return self.decode_response(
            super().post(
                path, data=data, content_type=content_type, secure=secure,
                locale=locale, **extra), method='post')

    def head(self, path, data=None, secure=False, locale=None, **extra):
        return self.decode_response(
            super().head(
                path, data=data, secure=secure, locale=locale, **extra),
            method='head')

    def trace(self, path, secure=False, locale=None, **extra):
        return self.decode_response(super().trace(
            path, secure=secure, locale=locale, **extra), method='trace')

    def options(self, path, data='', content_type='application/json',
                secure=False, locale=None, **extra):
        return self.decode_response(
            super().options(
                path, data=data, content_type=content_type, secure=secure,
                locale=locale, **extra), method='options')

    def put(self, path, data='', content_type='application/json',
            secure=False, locale=None, **extra):
        return self.decode_response(
            super().put(
                path, data=data, content_type=content_type, secure=secure,
                locale=locale, **extra), method='put')

    def patch(self, path, data='', content_type='application/json',
              secure=False, locale=None, **extra):
        return self.decode_response(
            super().patch(
                path, data=data, content_type=content_type,
                secure=secure, locale=locale, **extra), method='patch')

    def delete(self, path, data='', content_type='application/json',
               secure=False, locale=None, **extra):
        return self.decode_response(
            super().delete(
                path, data=data, content_type=content_type, secure=secure,
                locale=locale, **extra), method='delete')


class TestAssertMixin:

    # assert response status code
    def assertRC(self, response, code, msg=None):
        msg = '\n'.join([msg or '', response.formatted()])
        return self.assertEqual(response.status_code, code, msg=msg)

    def format_json(self, src):
        if isinstance(src, dict):
            return json.dumps(src, indent=2)
        return src.formatted()

    def get_json(self, src):
        return src if isinstance(src, dict) else src.json_content

    def get_val(self, src, key, msg=None):
        def _p(k):
            return int(k[1:]) if k[0] == '@' else k

        try:
            return reduce(
                lambda c, k: c[_p(k)], key.split("."), self.get_json(src))
        except IndexError:
            assert False, f"'{key}' index not found in:" + msg
        except KeyError:
            assert False, f"'{key}' not found in:" + msg

    # assert JSON content at key equals value
    def assertJE(self, src, key, value, msg=None):
        msg = '\n'.join([msg or '', self.format_json(src)])
        return self.assertEqual(self.get_val(
            src, key, msg=msg), value, msg=msg)

    # assert JSON content at key not equals value
    def assertNJE(self, src, key, value, msg=None):
        msg = '\n'.join([msg or '', self.format_json(src)])
        return self.assertNotEqual(
            self.get_val(src, key, msg=msg), value, msg=msg)

    # assert JSON content at key exists
    def assertJEExists(self, src, key, msg=None):
        msg = '\n'.join([msg or '', self.format_json(src)])
        if '.' not in key:
            return self.assertIn(key, self.get_json(src), msg=msg)
        path, name = key.rsplit('.', 1)
        return self.assertIn(name, self.get_val(src, path, msg=msg), msg=msg)

    # assert JSON content at key not exists
    def assertJENotExists(self, src, key, msg=None):
        msg = '\n'.join([msg or '', self.format_json(src)])
        if '.' not in key:
            return self.assertNotIn(key, self.get_json(src), msg=msg)
        path, name = key.rsplit('.', 1)
        return self.assertNotIn(
            name, self.get_val(src, path, msg=msg), msg=msg)

    # assert JSON array size
    def assertSize(self, src, key, size, msg=None):
        msg = '\n'.join([msg or '', self.format_json(src)])
        return self.assertEqual(
            len(self.get_val(src, key, msg=msg)), size, msg=msg)

    # assert JSON array contains
    def assertJIn(self, src, key, element, msg=None):
        msg = '\n'.join([msg or '', self.format_json(src)])
        return self.assertIn(
            element, self.get_val(src, key, msg=msg), msg=msg)

    # assert JSON array contains
    def assertJNotIn(self, src, key, element, msg=None):
        msg = '\n'.join([msg or '', self.format_json(src)])
        return self.assertNotIn(
            element, self.get_val(src, key, msg=msg), msg=msg)


class TestPermsAssertMixin(TestAssertMixin):
    USER_TESTS = {}

    def assertPerms(self, **methods):
        ops = ['size']
        for method, result in methods.items():
            method_split = method.split('__')
            method = method_split.pop(0)
            op = (
                method_split and method_split[-1] in ops and
                method_split.pop(-1))
            test = '.'.join(method_split)
            with transaction.atomic():
                sid = transaction.savepoint()
                with self.subTest(msg=method):
                    response = getattr(self, method)()
                    msg = (
                        hasattr(self, '_logged_user') and
                        f"User {self._logged_user}" or None)
                    if test == 'count':
                        self.assertJE(response, 'meta.count', result, msg)
                        self.assertSize(response, 'items', result, msg)
                    elif test:
                        if op == 'size':
                            self.assertSize(response, test, result, msg)
                        else:
                            self.assertJE(response, test, result, msg)
                    else:
                        self.assertRC(response, result, msg)
                transaction.savepoint_rollback(sid)

    def test_all_users(self):
        for user, perms in self.USER_TESTS.items():
            self.client.login(username=user)
            self._logged_user = user
            self.assertPerms(**perms)


class MockBoto3Client:
    def generate_presigned_url(self, *args, **kwargs):
        params = kwargs.get('Params', {})
        return f"http://{params.get('Bucket')}/{params.get('Key')}"

    def head_object(self, *args, **kwargs):
        return dict(ContentLength=1000, ContentType="image/png")

    def delete_object(self, *args, **kwargs):
        pass
