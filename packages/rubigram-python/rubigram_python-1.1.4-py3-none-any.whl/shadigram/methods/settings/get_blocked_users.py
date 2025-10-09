import shadigram


class GetBlockedUsers:
    async def get_blocked_users(self: "shadigram.Client"):
        return await self.builder('getBlockedUsers')
