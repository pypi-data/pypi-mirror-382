from pfx.pfxcore.apidoc import QueryParameter, register_global_parameter


class ListSearch(QueryParameter):
    """Filter result by a text search.

    Apply the default text search (object-dependent).
    """
    name = 'search'
    schema = dict(type='string', default=None)


register_global_parameter(ListSearch)
