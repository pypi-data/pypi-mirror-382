from pfx.pfxcore.apidoc import QueryParameter, register_global_parameter


class ListCount(QueryParameter):
    """Total objects count in response (`meta.count`).

    * if `false` (default value), `meta.count` is not returned
    * if `true`, `meta.count` is returned

    If this attribute is set, `items` will be returned only if
    `items` attribute is explicitly `true`.
    """
    name = 'count'
    schema = dict(type='boolean', default=False)


register_global_parameter(ListCount)
