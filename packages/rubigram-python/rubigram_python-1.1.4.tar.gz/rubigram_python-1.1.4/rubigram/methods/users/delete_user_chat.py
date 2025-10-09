
from typing import Union
import rubigram


class DeleteUserChat:
    """
    Provides a method to delete a user chat.

    Methods:
    - delete_user_chat: Delete a user chat.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def delete_user_chat(
            self: "rubigram.Client",
            user_guid: str,
            last_message_id: Union[str, int],
    ) -> "rubigram.types.Update":
        """
        Delete a user chat.

        Args:
        - user_guid (str): The GUID of the user whose chat is to be deleted.
        - last_message_id (Union[str, int]): The last message ID.

        Returns:
        - The result of the user chat deletion.
        """
        return await self.builder('deleteUserChat',
                                  input={
                                      'last_deleted_message_id': last_message_id,
                                      'user_guid': user_guid
                                  })
