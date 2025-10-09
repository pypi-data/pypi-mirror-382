from pfx.pfxcore.apidoc import QueryParameter, register_global_parameter


class SubsetPage(QueryParameter):
    """The page number to query in `pagination` mode.

    If the value of `subset` is not `"pagination"`, this attribute will
    be ignored.
    """
    name = 'page'
    schema = dict(type='integer', default=1)


register_global_parameter(SubsetPage)
