from pfx.pfxcore.apidoc import QueryParameter, register_global_parameter


class SubsetPageSubset(QueryParameter):
    """The maximum number of pages in `pagination` mode.

    The maximum numb of pages in `meta.subset.subset` element.

    If the value of `subset` is not `"pagination"`, this attribute will
    be ignored.
    """
    name = 'page_subset'
    schema = dict(type='integer', default=5)


register_global_parameter(SubsetPageSubset)
