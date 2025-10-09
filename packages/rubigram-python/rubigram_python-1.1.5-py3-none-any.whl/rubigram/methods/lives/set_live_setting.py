import rubigram


class SetLiveSetting:
    """
    A class to manage live stream settings on Rubigram.
    """

    async def set_live_setting(
        self: "rubigram.Client",
        live_id: str,
        allow_comment: bool
    ) -> rubigram.types.Update:
        """
        Set the settings of a given live stream.

        Args:
            live_id (str): The unique identifier of the live stream.
            allow_comment (bool): Whether to allow comments on the live stream.

        Returns:
            rubigram.types.Update: The update response after applying settings.
        """
        return await self.builder(
            "setLiveSetting",
            input={
                "live_id": live_id,
                "allow_comment": allow_comment,
                "updated_parameters": ['allow_comment']
            },
        )
