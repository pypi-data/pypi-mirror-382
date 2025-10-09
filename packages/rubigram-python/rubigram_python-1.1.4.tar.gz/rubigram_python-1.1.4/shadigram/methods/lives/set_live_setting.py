import shadigram


class SetLiveSetting:
    """
    A class to manage live stream settings on shadigram.
    """

    async def set_live_setting(
        self: "shadigram.Client",
        live_id: str,
        allow_comment: bool
    ) -> shadigram.types.Update:
        """
        Set the settings of a given live stream.

        Args:
            live_id (str): The unique identifier of the live stream.
            allow_comment (bool): Whether to allow comments on the live stream.

        Returns:
            shadigram.types.Update: The update response after applying settings.
        """
        return await self.builder(
            "setLiveSetting",
            input={
                "live_id": live_id,
                "allow_comment": allow_comment,
                "updated_parameters": ['allow_comment']
            },
        )
