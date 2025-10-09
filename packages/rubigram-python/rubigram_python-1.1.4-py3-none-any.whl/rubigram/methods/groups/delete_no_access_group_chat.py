
import rubigram


class DeleteNoAccessGroupChat:
    async def delete_no_access_group_chat(
            self: "rubigram.Client",
            group_guid: str,
    ) -> rubigram.types.Update:
        """
        Delete a group chat that has no access.

        Args:
        - group_guid (str): The GUID of the group.

        Returns:
        - rubigram.types.Update: The result of the API call.
        """
        return await self.builder('deleteNoAccessGroupChat',
                                  input={
                                      'group_guid': group_guid,
                                  })
