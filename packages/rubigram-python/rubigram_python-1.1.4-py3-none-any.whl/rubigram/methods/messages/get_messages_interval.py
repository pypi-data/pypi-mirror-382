
from typing import Union
import rubigram


class GetMessagesInterval:
    """
    Provides a method to retrieve messages in an interval around a middle message ID.

    Methods:
    - get_messages_interval: Retrieve messages in an interval around a middle message ID.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def get_messages_interval(
            self: "rubigram.Client",
            object_guid: str,
            middle_message_id: Union[int, str],
    ) -> rubigram.types.Update:
        """
        Retrieve messages in an interval around a middle message ID.

        Parameters:
        - object_guid (str): The GUID of the object to which the messages belong.
        - middle_message_id (Union[int, str]): The middle message ID around which the interval is determined.

        Returns:
        - rubigram.types.Update: The retrieved messages in the specified interval.
        """
        return await self.builder('getMessagesInterval',
                                  input={
                                      'object_guid': object_guid,
                                      'middle_message_id': str(middle_message_id),
                                  })
