import shadigram


class GetMyStickerSets:
    async def get_my_sticker_sets(self: "shadigram.Client"):
        return await self.builder('getMyStickerSets')
