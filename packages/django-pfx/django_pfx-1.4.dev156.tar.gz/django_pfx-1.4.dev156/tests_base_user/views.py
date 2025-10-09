import logging

from pfx.pfxcore.decorator import rest_view
from pfx.pfxcore.models import PFXUser
from pfx.pfxcore.views import PermsRestView

logger = logging.getLogger(__name__)


@rest_view("/users")
class UserRestView(PermsRestView):
    model = PFXUser
    fields = ['first_name', 'last_name', 'username']
