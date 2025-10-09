
import shadigram


class StopLive:
    """
    A class to handle stopping a live stream on shadigram.
    """

    async def stop_live(
        self: "shadigram.Client",
        live_id: str
    ) -> "shadigram.types.Update":
        """
        Stop a given live stream.

        Args:
            live_id (str): The unique identifier of the live stream.

        Returns:
            shadigram.types.Update: The update response after stopping the live.
        """
        return await self.builder(
            "stopLive",
            input={
                "live_id": live_id
            },
        )
