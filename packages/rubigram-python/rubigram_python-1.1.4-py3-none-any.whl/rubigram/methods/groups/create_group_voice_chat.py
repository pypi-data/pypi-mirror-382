
import rubigram


class CreateGroupVoiceChat:
    async def create_group_voice_chat(
            self: "rubigram.Client",
            group_guid: str,
    ) -> rubigram.types.Update:
        """
        Create a voice chat in a group.

        Args:
        - group_guid (str): The GUID of the group.

        Returns:
        - rubigram.types.Update: The result of the API call.
        """
        return await self.builder('createGroupVoiceChat',
                                  input={
                                      'group_guid': group_guid,
                                  })
