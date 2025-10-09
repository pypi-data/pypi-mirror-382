
import rubigram


class DeleteNoAccessChannelChat:
    async def delete_no_access_group_chat(
            self: "rubigram.Client",
            channel_guid: str,
    ) -> rubigram.types.Update:
        """
        Delete a channel chat that has no access.

        Args:
        - channel_guid (str): The GUID of the channel.

        Returns:
        - rubigram.types.Update: The result of the API call.
        """
        return await self.builder('deleteNoAccessChannelChat',
                                  input={
                                      'channel_guid': channel_guid,
                                  })
