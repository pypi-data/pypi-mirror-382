import rubigram


class GetLivePlayUrl:
    """
    A class to fetch the play URL of a live stream on Rubigram.
    """


    async def get_live_play_url(
        self: "rubigram.Client",
        live_id: str,
        access_token: bool
    ) -> rubigram.types.Update:
        """
        Retrieve the play URL of a given live stream.

        Args:
            live_id (str): The unique identifier of the live stream.
            access_token (bool): Access token to authorize the request.

        Returns:
            rubigram.types.Update: The response containing the live play URL.
        """
        return await self.builder(
            "getLivePlayUrl",
            input={
                "live_id": live_id,
                "access_token": access_token,
            },
        )
