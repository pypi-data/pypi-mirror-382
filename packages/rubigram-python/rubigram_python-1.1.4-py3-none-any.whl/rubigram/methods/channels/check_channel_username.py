
import rubigram
from rubigram.types import Update


class CheckChannelUsername:
    async def check_channel_username(
        self: "rubigram.Client",
        username: str,
    ) -> Update:
        """
        Check the availability of a username for a channel.

        Parameters:
        - username (str): The username to check.

        Returns:
        rubigram.types.Update: The result of the API call.
        """
        return await self.builder(
            name='checkChannelUsername',
            input={'username': username.replace('@', '')}
        )
