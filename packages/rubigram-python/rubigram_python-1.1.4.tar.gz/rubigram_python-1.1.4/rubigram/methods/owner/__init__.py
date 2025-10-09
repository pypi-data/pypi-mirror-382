
from .change_object_owner import ChangeObjectOwner
from .reply_request_object_owner import ReplyRequestObjectOwner
from .cancel_change_object_owner import CancelChangeObjectOwner
from .get_pending_object_owner import GetPendingObjectOwner


class Owner(
    ChangeObjectOwner,
    ReplyRequestObjectOwner,
    CancelChangeObjectOwner,
    GetPendingObjectOwner
):
    pass
