
import rubigram


class GetBannedGroupMembers:
    async def get_banned_group_members(
            self: "rubigram.Client",
            group_guid: str,
            start_id: str = None,
    ) -> rubigram.types.Update:
        """
        Get the list of banned members in a group.

        Args:
        - group_guid (str): The GUID of the group.
        - start_id (Optional[str]): The starting ID for fetching results.

        Returns:
        - rubigram.types.Update: The result of the API call.
        """
        return await self.builder('getBannedGroupMembers',
                                  input={
                                      'group_guid': group_guid,
                                      'start_id': start_id,
                                  })
