
import rubigram


class StopBot:
    """
    Provides a method to stop a bot.

    Methods:
    - stop_bot: Stop a running bot.
    """

    async def stop_bot(
        self: "rubigram.Client",
        bot_guid: str
    ) -> rubigram.types.Update:
        """
        Stop a bot.

        Args:
        - bot_guid (str): The GUID of the bot.

        Returns:
        - The response containing the updated bot status.
        """
        return await self.builder(
            "stopBot",
            input={
                "bot_guid": bot_guid,
            }
        )
