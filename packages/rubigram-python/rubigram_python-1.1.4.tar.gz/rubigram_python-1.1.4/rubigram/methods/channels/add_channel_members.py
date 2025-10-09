
import rubigram
from typing import Union
from rubigram.types import Update


class AddChannelMembers:
    async def add_channel_members(
        self: "rubigram.Client",
        channel_guid: str,
        member_guids: Union[str, list],
    ) -> Update:
        """
        Add members to a channel.

        Parameters:
        - channel_guid (str): The unique identifier of the channel.
        - member_guids (Union[str, list]): The unique identifier(s) of the member(s) to be added.

        Returns:
        rubigram.types.Update: The result of the API call.
        """
        if isinstance(member_guids, str):
            member_guids = [member_guids]

        return await self.builder(
            'addChannelMembers',
            input={
                'channel_guid': channel_guid,
                'member_guids': member_guids,
            }
        )
