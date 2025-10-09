
from .action_on_join_request import ActionOnJoinRequest
from .get_join_requests import GetJoinRequests
from .create_join_link import CreateJoinLink
from .get_join_links import GetJoinLinks


class Links(
        ActionOnJoinRequest,
        GetJoinRequests,
        CreateJoinLink,
        GetJoinLinks
):
    pass
