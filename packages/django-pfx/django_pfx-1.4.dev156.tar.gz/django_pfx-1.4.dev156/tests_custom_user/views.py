import logging

from pfx.pfxcore.decorator import rest_view
from pfx.pfxcore.views import RestView
from tests_custom_user.models import User

logger = logging.getLogger(__name__)


@rest_view("/users")
class UserRestView(RestView):
    model = User
    fields = ['username']
