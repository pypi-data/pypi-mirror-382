from pfx.pfxcore.apidoc import QueryParameter, register_global_parameter


class DateFormat(QueryParameter):
    """Date format option.

    * if `false` (default value), date fields will be returned
    as ISO 8601 string.
    * if `true`, date fields will be returned as a JSON object with
    2 attributes:
        * `value`: the ISO 8601 string
        * `formatted`: a string representation
        (short format using the request locale)
    """
    name = 'date_format'
    schema = dict(type='boolean', default=False)


register_global_parameter(DateFormat)
