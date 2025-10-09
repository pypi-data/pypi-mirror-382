import shadigram


class BanMember:
    async def ban_member(
            self: "shadigram.Client",
            object_guid: str,
            member_guid: str,
    ):
        if object_guid.startswith('g0'):
            return await self.ban_group_member(object_guid, member_guid)
        elif object_guid.startswith('c0'):
            return await self.ban_channel_member(object_guid, member_guid)
