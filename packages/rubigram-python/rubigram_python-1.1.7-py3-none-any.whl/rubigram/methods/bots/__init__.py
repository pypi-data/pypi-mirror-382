
from .delete_bot_chat import DeleteBotChat
from .get_bot_info import GetBotInfo
from .stop_bot import StopBot


class Bots(
    DeleteBotChat,
    GetBotInfo,
    StopBot
):
    pass
