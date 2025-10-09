
from typing import Union
import rubigram


class DeleteBotChat:
    """
    Provides a method to delete a bot chat.

    Methods:
    - delete_bot_chat: Delete a bot chat.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def delete_bot_chat(
        self: "rubigram.Client",
        bot_guid: str,
        last_message_id: Union[str, int],
    ) -> rubigram.types.Update:
        """
        Delete a bot chat.

        Args:
        - bot_guid (str): The GUID of the bot whose chat is to be deleted.
        - last_message_id (Union[str, int]): The last deleted message ID.

        Returns:
        - The result of the bot chat deletion.
        """
        return await self.builder(
            "deleteBotChat",
            input={
                "bot_guid": bot_guid,
                "last_deleted_message_id": last_message_id,
            }
        )
