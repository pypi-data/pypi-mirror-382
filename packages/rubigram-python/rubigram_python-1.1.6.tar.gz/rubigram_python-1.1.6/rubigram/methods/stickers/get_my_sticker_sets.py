
import rubigram


class GetMyStickerSets:
    """
    Provides a method to get the sticker sets owned by the user.

    Methods:
    - get_my_sticker_sets: Get the sticker sets owned by the user.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def get_my_sticker_sets(
            self: "rubigram.Client") -> "rubigram.types.Update":
        """
        Get the sticker sets owned by the user.

        Returns:
        - The sticker sets owned by the user.
        """
        return await self.builder('getMyStickerSets')
