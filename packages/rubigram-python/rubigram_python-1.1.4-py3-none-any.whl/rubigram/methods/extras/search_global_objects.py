
import rubigram


class SearchGlobalObjects:
    async def search_global_objects(
            self: "rubigram.Client",
            search_text: str,
    ) -> rubigram.types.Update:
        """
        Search for global objects (users, channels, etc.) based on the given search text.

        Args:
            search_text (str): The text to search for.

        Returns:
            rubigram.types.Update: The update containing search results.
        """
        return await self.builder('searchGlobalObjects',
                                  input={
                                      'search_text': search_text,
                                  })
