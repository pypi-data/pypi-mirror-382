
import rubigram


class GetUpdates:
    async def get_updates(self: "rubigram.Client") -> "rubigram.types.Update":
        """
        Get updates from the server.

        Returns:
        - rubigram.types.Update: An Update object containing information about the updates.
        """

        return await self.connection.get_updates()
