from .mixins import *


class CRUDMixin(
    Create[RESPONSE_PROTOCOL],
    Retrieve[RESPONSE_PROTOCOL],
    Update[RESPONSE_PROTOCOL],
    Delete,
    Generic[RESPONSE_PROTOCOL],
):
    pass
