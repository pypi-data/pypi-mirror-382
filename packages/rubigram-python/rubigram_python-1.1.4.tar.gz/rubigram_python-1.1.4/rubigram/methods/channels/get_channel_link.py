
import rubigram
from rubigram.types import Update


class GetChannelLink:
    async def get_channel_link(
            self: "rubigram.Client",
            channel_guid: str,
    ) -> Update:
        """
        Get the join link of a channel.

        Parameters:
        - channel_guid (str): The GUID of the channel.

        Returns:
        rubigram.types.Update: The result of the API call.
        """
        return await self.builder('getChannelLink', input={'channel_guid': channel_guid})
