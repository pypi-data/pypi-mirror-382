
import rubigram


class GetLiveStatus:
    """
    A class to handle fetching the status of a live stream from Rubigram.
    """

    async def get_live_status(
        self,
        live_id: str,
        access_token: str
    ) -> rubigram.types.Update:
        """
        Retrieve the status of a given live stream.

        Args:
            live_id (str): The unique identifier of the live stream.
            access_token (str): The access token required to authenticate the request.

        Returns:
            rubigram.types.Update: The update response containing live status data.
        """
        return await self.builder(
            'getLiveStatus',
            input={
                'live_id': live_id,
                'access_token': access_token
            }
        )
