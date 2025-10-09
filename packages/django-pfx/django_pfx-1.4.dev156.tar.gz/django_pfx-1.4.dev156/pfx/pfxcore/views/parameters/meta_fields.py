from pfx.pfxcore.apidoc import QueryParameter, register_global_parameter


class MetaFields(QueryParameter):
    """if `true`, `fields` list is returned in response.

    if one query parameter is set, the default value is `false`.
    """
    name = 'fields'
    schema = dict(type='boolean', default=True)


register_global_parameter(MetaFields)
