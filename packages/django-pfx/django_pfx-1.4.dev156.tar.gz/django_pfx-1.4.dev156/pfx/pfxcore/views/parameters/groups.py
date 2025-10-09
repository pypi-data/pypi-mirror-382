from pfx.pfxcore.apidoc import ParameterGroup

# from .date_format import DateFormat
from .list_count import ListCount
from .list_items import ListItems
from .list_mode import ListMode
from .list_order import ListOrder
from .list_search import ListSearch
from .meta_fields import MetaFields
from .meta_filters import MetaFilters
from .meta_orders import MetaOrders
from .subset import Subset
from .subset_limit import SubsetLimit
from .subset_offset import SubsetOffset
from .subset_page import SubsetPage
from .subset_page_size import SubsetPageSize
from .subset_page_subset import SubsetPageSubset


class ModelSerialization(ParameterGroup):
    # TODO: check the need of this params, if needed it should be better
    # to allow to choose format : iso/short/long (for instance).
    # For this reason we choose to not export it in apidoc.
    # parameters = [DateFormat]
    parameters = []


class MetaList(ParameterGroup):
    """Parameters group for meta list services."""
    parameters = [MetaFields, MetaFilters, MetaOrders]


class List(ParameterGroup):
    """Parameters group for list services."""
    parameters = [
        ListCount, ListItems, ListSearch, ListOrder, ListMode,
        Subset, SubsetPage, SubsetPageSize,
        SubsetPageSubset, SubsetOffset, SubsetLimit]
