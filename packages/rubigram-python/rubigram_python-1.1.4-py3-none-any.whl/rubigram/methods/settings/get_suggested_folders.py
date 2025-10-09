
import rubigram
from rubigram.types import Update


class GetSuggestedFolders:
    """
    Provides a method to get the suggested folders for the user.

    Methods:
    - get_suggested_folders: Get the suggested folders for the user.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def get_suggested_folders(
            self: "rubigram.Client"
    ) -> Update:
        """
        Get the suggested folders for the user.

        Returns:
        - rubigram.types.Update: The suggested folders for the user.
        """
        return await self.builder('getSuggestedFolders')  # type: ignore
