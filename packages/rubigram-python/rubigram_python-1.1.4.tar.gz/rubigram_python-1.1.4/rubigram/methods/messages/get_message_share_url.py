
import rubigram


class GetMessageShareUrl:
    """
    Provides a method to get the shareable URL of a specific message.

    Methods:
    - get_message_url: Get the shareable URL of a specific message.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def get_message_url(
            self: "rubigram.Client",
            object_guid: str,
            message_id: str,
    ) -> rubigram.types.Update:
        """
        Get the shareable URL of a specific message.

        Parameters:
        - object_guid (str): The GUID of the object to which the message belongs.
        - message_id (str): The ID of the message for which to retrieve the shareable URL.

        Returns:
        - rubigram.types.Update: The shareable URL of the specified message.
        """
        input = dict(
            object_guid=object_guid,
            message_id=message_id,
        )

        return await self.builder(name='getMessageShareUrl',
                                  input=input)
