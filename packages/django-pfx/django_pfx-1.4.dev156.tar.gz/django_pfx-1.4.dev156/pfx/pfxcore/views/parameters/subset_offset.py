from pfx.pfxcore.apidoc import QueryParameter, register_global_parameter


class SubsetOffset(QueryParameter):
    """The first object index to retrieve in `offset` mode.

    If the value of `subset` is not `"offset"`, this attribute will
    be ignored.
    """
    name = 'offset'
    schema = dict(type='integer', default=0)


register_global_parameter(SubsetOffset)
