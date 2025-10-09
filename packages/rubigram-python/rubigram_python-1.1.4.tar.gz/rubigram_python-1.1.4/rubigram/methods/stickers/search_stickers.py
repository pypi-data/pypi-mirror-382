
import rubigram


class SearchStickers:
    """
    Provides a method to search for stickers.

    Methods:
    - search_stickers: Search for stickers.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def search_stickers(
            self: "rubigram.Client",
            search_text: str = '',
            start_id: str = None,
    ) -> rubigram.types.Update:
        """
        Search for stickers.

        Parameters:
        - search_text (str): The search text.
        - start_id (str): The start ID for pagination.

        Returns:
        - Stickers matching the search criteria.
        """
        return await self.builder('searchStickers',
                                  input={
                                      'search_text': search_text,
                                      'start_id': str(start_id),
                                  })
