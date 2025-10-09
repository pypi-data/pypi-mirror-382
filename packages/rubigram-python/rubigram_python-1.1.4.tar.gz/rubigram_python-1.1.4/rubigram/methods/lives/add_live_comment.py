
import rubigram


class AddLiveComment:
    """
    A class to handle adding comments to a Rubigram live stream.
    """

    async def add_live_comment(
        self,
        live_id: str,
        access_token: str,
        text: str
    ) -> rubigram.types.Update:
        """
        Add a comment to a given live stream.

        Args:
            live_id (str): The unique identifier of the live stream.
            access_token (str): The access token required to authenticate the request.
            text (str): The comment text to be added.

        Returns:
            rubigram.types.Update: The update response confirming the comment was added.
        """
        return await self.builder(
            'addLiveComment',
            input={
                'live_id': live_id,
                'access_token': access_token,
                'text': text
            }
        )
