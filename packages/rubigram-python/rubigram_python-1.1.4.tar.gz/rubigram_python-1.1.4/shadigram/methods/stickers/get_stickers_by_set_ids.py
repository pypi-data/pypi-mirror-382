from typing import Union
import shadigram


class GetStickersBySetIDs:
    async def GetStickersBySetIDs(
            self: "shadigram.Client",
            sticker_set_ids: Union[str, list],
    ):
        if isinstance(sticker_set_ids, str):
            sticker_set_ids = [str(sticker_set_ids)]

        return await self.builder(name='GetStickersBySetIDs',
                                  input={'sticker_set_ids': sticker_set_ids})
