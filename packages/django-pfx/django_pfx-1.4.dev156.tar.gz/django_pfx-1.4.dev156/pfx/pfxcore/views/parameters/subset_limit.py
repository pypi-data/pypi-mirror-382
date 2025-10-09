from pfx.pfxcore.apidoc import QueryParameter, register_global_parameter


class SubsetLimit(QueryParameter):
    """The maximum number of objects in `offset` mode.

    If the value of `subset` is not `"offset"`, this attribute will
    be ignored.

    If `limit` > `PFX_MAX_LIST_RESULT_SIZE`, `PFX_MAX_LIST_RESULT_SIZE`
    will be applied.
    """
    name = 'limit'
    schema = dict(type='integer', default=10)


register_global_parameter(SubsetLimit)
