from pfx.pfxcore.apidoc import QueryParameter, register_global_parameter


class SubsetPageSize(QueryParameter):
    """The maximum number of objects in `pagination` mode.

    If the value of `subset` is not `"pagination"`, this attribute will
    be ignored.

    If `page_size` > `PFX_MAX_LIST_RESULT_SIZE`, `PFX_MAX_LIST_RESULT_SIZE`
    will be applied.
    """
    name = 'page_size'
    schema = dict(type='integer', default=10)


register_global_parameter(SubsetPageSize)
