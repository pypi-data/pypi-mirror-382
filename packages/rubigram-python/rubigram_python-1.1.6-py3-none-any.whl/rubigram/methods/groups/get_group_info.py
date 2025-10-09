
import rubigram


class GetGroupInfo:
    async def get_group_info(
            self,
            group_guid: str,
    ) -> rubigram.types.Update:
        """
        Get information about a group.

        Args:
        - group_guid (str): The GUID of the group.

        Returns:
        - rubigram.types.Update: Update object containing information about the group.
        """
        return await self.builder('getGroupInfo',
                                  input={
                                      'group_guid': group_guid,
                                  })
