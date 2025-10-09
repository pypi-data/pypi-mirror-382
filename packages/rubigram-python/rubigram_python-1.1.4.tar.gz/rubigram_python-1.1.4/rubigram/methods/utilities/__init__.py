
from .start import Start
from .connect import Connect
from .disconnect import Disconnect
from .add_handler import AddHandler
from .remove_handler import RemoveHandler
from .run import Run
from .upload import UploadFile
from .download import Download
from .get_updates import GetUpdates
from .download_profile_picture import DownloadProfilePicture
from .get_members import GetMembers
from .typewriter import Typewriter
from .colors import Colors
from .progress import Progress


class Utilities(
    Start,
    Connect,
    Disconnect,
    AddHandler,
    RemoveHandler,
    Run,
    UploadFile,
    Download,
    GetUpdates,
    DownloadProfilePicture,
    GetMembers,
    Typewriter,
    Colors,
    Progress
):
    pass
