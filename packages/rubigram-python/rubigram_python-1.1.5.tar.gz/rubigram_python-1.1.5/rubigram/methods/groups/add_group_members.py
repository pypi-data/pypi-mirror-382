
import rubigram
from typing import Union


class AddGroupMembers:
    async def add_group_members(
            self: "rubigram.Client",
            group_guid: str,
            member_guids: Union[str, list],
    ) -> "rubigram.types.Update":
        """
        Adds one or more members to a group.

        Args:
            group_guid (str): The GUID of the group.
            member_guids (Union[str, list]): A single member GUID or a list of member GUIDs to be added.

        Returns:
            rubigram.types.Update: An update object indicating the result of the operation.
        """
        if isinstance(member_guids, str):
            member_guids = [member_guids]

        return await self.builder('addGroupMembers',
                                  input={
                                      'group_guid': group_guid,
                                      'member_guids': member_guids,
                                  })
