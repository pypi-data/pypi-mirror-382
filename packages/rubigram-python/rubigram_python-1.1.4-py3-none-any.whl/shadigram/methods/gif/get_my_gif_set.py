import shadigram


class GetMyGifSet:
    async def get_my_gif_set(self: "shadigram.Client"):
        return await self.builder('getMyGifSet')
