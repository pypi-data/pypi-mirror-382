from pfx.pfxcore.apidoc import QueryParameter, register_global_parameter


class ListItems(QueryParameter):
    """List of objects in response (`items`).

    * if `true` (default value), `items` is returned
    * if `false`, `items` is not returned

    If `count` attribute is set, the default value is `false`.
    """
    name = 'items'
    schema = dict(type='boolean', default=True)


register_global_parameter(ListItems)
