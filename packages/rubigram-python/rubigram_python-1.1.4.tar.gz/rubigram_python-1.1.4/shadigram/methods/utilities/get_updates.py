import shadigram


class GetUpdates:
    async def get_updates(self: "shadigram.Client"):
        return await self.connection.get_updates()
