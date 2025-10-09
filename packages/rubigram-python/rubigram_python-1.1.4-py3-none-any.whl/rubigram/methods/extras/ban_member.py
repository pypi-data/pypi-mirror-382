
import rubigram


class BanMember:
    async def ban_member(
            self: "rubigram.Client",
            object_guid: str,
            member_guid: str,
    ) -> rubigram.types.Update:
        """
        Ban a member from a group or channel.

        Args:
            object_guid (str): The GUID of the group or channel.
            member_guid (str): The GUID of the member to be banned.

        Returns:
            rubigram.types.Update: The update after banning the member.
        """
        if object_guid.startswith('g0'):
            return await self.ban_group_member(object_guid, member_guid)
        elif object_guid.startswith('c0'):
            return await self.ban_channel_member(object_guid, member_guid)
