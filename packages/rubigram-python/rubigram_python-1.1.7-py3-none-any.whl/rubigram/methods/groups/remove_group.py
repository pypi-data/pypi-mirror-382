
import rubigram


class RemoveGroup:
    async def remove_group(
            self: "rubigram.Client",
            group_guid: str,
    ) -> rubigram.types.Update:
        """
        Remove a group.

        Args:
        - group_guid (str): The GUID of the group.

        Returns:
        - rubigram.types.Update: Update object confirming the removal of the group.
        """
        return await self.builder('removeGroup', input={'group_guid': group_guid})
