
import random
import rubigram


class SendLive:
    """
    Provides a method to send a live stream message.

    Methods:
    - send_live: Send a live stream with given parameters.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def send_live(
        self: "rubigram.Client",
        object_guid: str,
        title: str,
        device_type: str = "Software",
        thumb_inline: str = None,
    ) -> rubigram.types.Update:
        """
        Send a live stream message.

        Parameters:
        - object_guid (str): The GUID of the object (e.g., channel, user).
        - title (str): Title of the live stream.
        - device_type (str): Type of device sending the live, default is "Software".
        - thumb_inline (str): Thumbnail inline data.

        Returns:
        - rubigram.types.Update: The update response from the API.
        """
        rnd = str(random.randint(100000, 999999))

        return await self.builder(
            'sendLive',
            input={
                'object_guid': object_guid,
                'title': title,
                'device_type': device_type,
                'thumb_inline': thumb_inline,
                'rnd': rnd,
            }
        )
