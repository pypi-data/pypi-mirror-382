
import rubigram


class GetMyGifSet:
    async def get_my_gif_set(
            self: "rubigram.Client"
    ) -> rubigram.types.Update:
        """
        Gets the user's personal GIF set.

        Returns:
            rubigram.types.Update: Information about the user's GIF set.
        """
        return await self.builder('getMyGifSet')
