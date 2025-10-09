from pfx.pfxcore.apidoc import QueryParameter, register_global_parameter


class ListMode(QueryParameter):
    """Mode of result list.

    * If `"list"` (default value): Full object representation for lists.
    * If `"select"`: Minimal object representation for select widget.
    """
    name = 'mode'
    schema = dict(type='string', default='list', enum=['list', 'select'])


register_global_parameter(ListMode)
