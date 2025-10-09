
import rubigram
from typing import Union
from rubigram.types import Update


class EditFolder:
    """
    A class for editing existing folders in Rubika.

    This class provides methods to modify folder properties, such as adding or removing objects.
    """

    async def edit_folder(
        self: "rubigram.Client",
        folder_id: str,
        exclude_object_guids: Union[str, list] = None,
    ) -> Update:
        """
        Edit an existing folder by updating its properties.

        Parameters:
        - folder_id (str): The ID of the folder to be edited.
        - exclude_object_guids (Union[str, list], optional): The GUID(s) of the objects (e.g., groups) to be removed from the folder.

        Returns:
        - rubigram.types.Update: The result of the API request.
        """
        # Prepare the input data for the API request
        input_data = {
            'folder_id': folder_id,
            'updated_parameters': ['exclude_object_guids'],
            'exclude_object_guids': exclude_object_guids,
        }

        # Call the builder method to send the API request
        return await self.builder('editFolder', input=input_data)
