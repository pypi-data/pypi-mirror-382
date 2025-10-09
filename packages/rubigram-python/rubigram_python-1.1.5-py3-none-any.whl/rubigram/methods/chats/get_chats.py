
import rubigram
from typing import Optional
from rubigram.types import Update


class GetChats:
    async def get_chats(
            self: "rubigram.Client",
            start_id: Optional[str] = None,
    ) -> Update:
        """
        Get a list of chats.

        Parameters:
        - start_id (Optional[str]): The ID to start from. If not provided, it starts from the
          beginning.

        Returns:
        rubigram.types.Update: The result of the API call, representing a list of chats.
        """
        return await self.builder(name='getChats', input={'start_id': start_id})
