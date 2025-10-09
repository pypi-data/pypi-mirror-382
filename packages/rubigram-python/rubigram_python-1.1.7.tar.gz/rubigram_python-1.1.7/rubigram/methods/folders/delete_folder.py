
import rubigram
from rubigram.types import Update


class DeleteFolder:
    """
    A class for deleting folders in Rubika.

    This class provides methods to manage folders in the Rubika application.
    """

    async def add_channel(
        self: "rubigram.Client",
        folder_id: str
    ) -> Update:
        """
        Delete a folder from Rubika.

        Parameters:
        - folder_id (str): The ID of the folder to be deleted.

        Returns:
        - rubigram.types.Update: The result of the API request.
        """
        input_data = {'folder_id': folder_id}
        return await self.builder('deleteFolder', input=input_data)
