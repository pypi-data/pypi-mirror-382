
from .delete_folder import DeleteFolder
from .add_folder import AddFolder
from .get_folders import GetFolders
from .edit_folder import EditFolder


class Folders(
    DeleteFolder,
    AddFolder,
    GetFolders,
    EditFolder
):
    pass
