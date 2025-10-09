from pfx.pfxcore.apidoc import QueryParameter, register_global_parameter


class MetaFilters(QueryParameter):
    """if `true`, `filters` list is returned in response.

    if one query parameter is set, the default value is `false`.
    """
    name = 'filters'
    schema = dict(type='boolean', default=True)


register_global_parameter(MetaFilters)
