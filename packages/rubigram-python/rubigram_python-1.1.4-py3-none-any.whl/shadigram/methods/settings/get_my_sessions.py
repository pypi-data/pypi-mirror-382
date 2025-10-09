import shadigram


class GetMySessions:
    async def get_my_sessions(self: "shadigram.Client"):
        return await self.builder('getMySessions')
