
import rubigram


class GetLiveComments:
    """
    A class to handle fetching live comments from Rubigram live streams.
    """

    async def get_live_comments(
        self,
        live_id: str,
        access_token: str,
        start_id: str = None
    ) -> rubigram.types.Update:
        """
        Retrieve live comments for a given live stream.

        Args:
            live_id (str): The unique identifier of the live stream.
            access_token (str): The access token required to authenticate the request.
            start_id (str, optional): The comment ID to start retrieving from. Defaults to None.

        Returns:
            rubigram.types.Update: The update response containing live comments data.
        """
        return await self.builder(
            'getLiveComments',
            input={
                'live_id': live_id,
                'access_token': access_token,
                'start_id': start_id
            }
        )
