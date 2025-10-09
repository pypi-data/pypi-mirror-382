
import rubigram


class GetBotInfo:
    """
    Provides a method to get bot information.

    Methods:
    - get_bot_info: Retrieve information about a specific bot.
    """

    async def get_bot_info(
        self: "rubigram.Client",
        bot_guid: str
    ) -> rubigram.types.Update:
        """
        Get information about a bot.

        Args:
        - bot_guid (str): The GUID of the bot.

        Returns:
        - The bot information response.
        """
        return await self.builder(
            "getBotInfo",
            input={
                "bot_guid": bot_guid,
            }
        )
