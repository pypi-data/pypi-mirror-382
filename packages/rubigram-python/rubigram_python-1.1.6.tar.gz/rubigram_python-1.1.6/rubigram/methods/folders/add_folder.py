
import rubigram
from typing import Union
from rubigram.types import Update


class AddFolder:
    """
    A class for adding folders in Rubika.

    This class provides methods to create new folders and manage their content in Rubika.
    """

    async def add_folder(
        self: "rubigram.Client",
        name: str,
        include_chat_types: list,
        exclude_chat_types: list,
        include_object_guids: Union[str, list],
        exclude_object_guids: Union[str, list],
        is_add_to_top: bool
    ) -> Update:
        """
        Create a new folder in Rubika with specified chat types and objects.

        Parameters:
        - name (str): The name of the new folder.
        - include_chat_types (list): Types of chats to include in the folder.
        - exclude_chat_types (list): Types of chats to exclude from the folder.
        - include_object_guids (Union[str, list]): GUIDs of objects (chats, groups, etc.) to include.
        - exclude_object_guids (Union[str, list]): GUIDs of objects to exclude from the folder.
        - is_add_to_top (bool): If True, adds the folder to the top of the list.

        Returns:
        - rubigram.types.Update: The result of the API request.
        """
        input_data = {
            'name': name,
            'include_chat_types': include_chat_types,
            'exclude_chat_types': exclude_chat_types,
            'include_object_guids': include_object_guids,
            'exclude_object_guids': exclude_object_guids,
            'is_add_to_top': is_add_to_top
        }
        return await self.builder('addFolder', input=input_data)
