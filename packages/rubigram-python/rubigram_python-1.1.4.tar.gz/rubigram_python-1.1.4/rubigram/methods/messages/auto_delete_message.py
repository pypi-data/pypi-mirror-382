
import rubigram
import asyncio
from typing import Union


class AutoDeleteMessage:
    """
    Provides a method to automatically delete a message after a specified time.

    Methods:
    - auto_delete_message: Automatically delete a message after a specified time.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def auto_delete_message(
            self: "rubigram.Client",
            object_guid: str,
            message_id: str,
            time: Union[float, int],
    ) -> rubigram.types.Update:
        """
        Automatically delete a message after a specified time.

        Parameters:
        - object_guid (str): The GUID of the object associated with the message (e.g., user, group, channel).
        - message_id (str): The ID of the message to be deleted.
        - time (Union[float, int]): The time delay (in seconds) before deleting the message.

        Returns:
        - rubigram.types.Update: The updated information after deleting the message.
        """
        await asyncio.sleep(time)
        return await self.delete_messages(object_guid, message_id)
