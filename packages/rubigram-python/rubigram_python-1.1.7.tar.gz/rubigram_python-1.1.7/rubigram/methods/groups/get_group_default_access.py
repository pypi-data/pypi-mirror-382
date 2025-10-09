
import rubigram


class GetGroupDefaultAccess:
    async def get_group_default_access(
            self,
            group_guid: str,
    ) -> rubigram.types.Update:
        """
        Get the default access settings for a group.

        Args:
        - group_guid (str): The GUID of the group.

        Returns:
        - rubigram.types.Update: Update object containing information about the default access settings.
        """
        return await self.builder('getGroupDefaultAccess',
                                  input={
                                      'group_guid': group_guid,
                                  })
