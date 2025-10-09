from pfx.pfxcore.apidoc import QueryParameter, register_global_parameter


class MetaOrders(QueryParameter):
    """if `true`, `orders` list is returned in response.

    if one query parameter is set, the default value is `false`.
    """
    name = 'orders'
    schema = dict(type='boolean', default=True)


register_global_parameter(MetaOrders)
