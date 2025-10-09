from pfx.pfxcore.apidoc import QueryParameter, register_global_parameter


class ListOrder(QueryParameter):
    """Control the order of objects in result.

    A comma separated list of field, optionally prefixed by :
    * `+` (default) : in ascending order.
    * `-` : in descending order.

    Exemple: `order=-date,name` (`order=-date,+name` is equivalent).

    The list of usable fields can be found in `/meta/list` service response.
    """
    name = 'order'
    schema = dict(type='string', default=None)


register_global_parameter(ListOrder)
