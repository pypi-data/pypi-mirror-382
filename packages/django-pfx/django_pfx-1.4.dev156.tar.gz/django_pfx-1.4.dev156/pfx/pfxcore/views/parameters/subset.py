from pfx.pfxcore.apidoc import QueryParameter, register_global_parameter


class Subset(QueryParameter):
    """Subset mode for objects list.

    * if `null` (default value), you receive a list of objects
    without subsets management.
    * if `"pagination"`, you receive a list of objects
    with pagination management (see parameters:
    `page`, `page_size`, `page_subset`). The following attributes are add
    to `meta.subset` in response :
        * `page` : the page number
        * `page_size` : the max number of objets per pages
        * `count` : the total number of objects
        * `page_count` : the total number of pages
        * `subset` : a limited list of page numbers (for paginator)
        * `page_subset` : max number of pages in `subset`
    * if `"offset"`, you receive a list of objects. The following attributes
    are add to `meta.subset` in response :
        * `count` : the total number of objects
        * `page_count` : the total number of pages
        * `limit` : the max number of objets in result
        * `offset` : the first object index in result
    with offset management (see parameters: `page_size`)

    The `PFX_MAX_LIST_RESULT_SIZE` will always be applied is set to limit
    the result list size.
    """
    name = 'subset'
    schema = dict(
        type='string', default=None, enum=['pagination', 'offset', None])


register_global_parameter(Subset)
