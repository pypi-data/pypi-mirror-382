
import rubigram
from rubigram.types import Update


class GetChannelAdminAccessList:
    async def get_channel_admin_access_list(
            self: "rubigram.Client",
            channel_guid: str,
            member_guid: str,
    ) -> Update:
        """
        Get the admin access list for a specific member in a channel.

        Parameters:
        - channel_guid (str): The GUID of the channel.
        - member_guid (str): The GUID of the member.

        Returns:
        rubigram.types.Update: The result of the API call.
        """
        return await self.builder('getChannelAdminAccessList', input={'channel_guid': channel_guid, 'member_guid': member_guid})
