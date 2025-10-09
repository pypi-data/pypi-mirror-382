import inspect
import re

RE_CAMEL_CASE = s = re.compile(r"(_|-)+")


def camel_case(s):
    s = RE_CAMEL_CASE.sub(" ", s).title().replace(" ", "")
    return ''.join([s[0].lower(), s[1:]])


class ParameterGroup():
    parameters = []


class Parameter:
    _group = None

    @classmethod
    def id(cls):
        return cls.__name__

    @classmethod
    def as_parameter(cls, doc=None):
        res = dict(name=cls.name)
        res['in'] = cls.location
        description = doc or inspect.getdoc(cls)
        if description:
            res['description'] = description
        members = inspect.getmembers(
            cls, predicate=lambda x: not (
                inspect.ismethod(x)))
        for name, value in members:
            if name.startswith('_') or name == 'location':
                continue
            res[camel_case(name)] = value
        return res


class QueryParameter(Parameter):
    location = 'query'


def register_global_parameter(parameter):
    from . import __PARAMETERS__
    __PARAMETERS__.append(parameter)
