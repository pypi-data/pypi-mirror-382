
from .add_live_comment import AddLiveComment
from .get_live_comments import GetLiveComments
from .get_live_status import GetLiveStatus
from .set_live_setting import SetLiveSetting
from .send_live import SendLive
from .stop_live import StopLive
from .get_live_play_url import GetLivePlayUrl


class Lives(
    AddLiveComment,
    GetLiveComments,
    GetLiveStatus,
    SetLiveSetting,
    SendLive,
    StopLive,
    GetLivePlayUrl
):
    pass
