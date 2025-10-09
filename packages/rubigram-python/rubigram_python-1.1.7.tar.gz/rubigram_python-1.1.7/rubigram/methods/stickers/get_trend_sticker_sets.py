
import rubigram


class GetTrendStickerSets:
    """
    Provides a method to get trending sticker sets.

    Methods:
    - get_trend_sticker_sets: Get trending sticker sets.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def get_trend_sticker_sets(
            self: "rubigram.Client",
            start_id: str = None,
    ) -> rubigram.types.Update:
        """
        Get trending sticker sets.

        Parameters:
        - start_id (str): The start ID for pagination.

        Returns:
        - Trending sticker sets.
        """
        return await self.builder(name='getTrendStickerSets',
                                  input={'start_id': str(start_id) if start_id is not None else None})
