
import rubigram


class StopLive:
    """
    A class to handle stopping a live stream on Rubigram.
    """

    async def stop_live(
        self: "rubigram.Client",
        live_id: str
    ) -> "rubigram.types.Update":
        """
        Stop a given live stream.

        Args:
            live_id (str): The unique identifier of the live stream.

        Returns:
            rubigram.types.Update: The update response after stopping the live.
        """
        return await self.builder(
            "stopLive",
            input={
                "live_id": live_id
            },
        )
