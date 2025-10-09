
from typing import Optional
import rubigram
from rubigram.types import Update


class GetBannedChannelMembers:
    async def get_banned_channel_members(
            self: "rubigram.Client",
            channel_guid: str,
            start_id: Optional[str] = None,
    ) -> Update:
        """
        Get a list of banned members in a group.

        Parameters:
        - group_guid (str): The GUID of the group.
        - start_id (str, optional): The ID to start retrieving banned members from.

        Returns:
        rubigram.types.Update: The result of the API call.
        """
        return await self.builder('getBannedChannelMembers', input={'channel_guid': channel_guid, 'start_id': start_id})
