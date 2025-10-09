from pfx.pfxcore.apidoc import QueryParameter, register_global_parameter


class MediaRedirect(QueryParameter):
    """if `true`, make a redirect, otherwise return the file URL.
    """
    name = 'redirect'
    schema = dict(type='boolean', default=False)


register_global_parameter(MediaRedirect)
