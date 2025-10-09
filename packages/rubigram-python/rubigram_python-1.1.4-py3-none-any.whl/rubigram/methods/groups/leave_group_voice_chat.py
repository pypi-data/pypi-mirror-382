
import rubigram


class LeaveGroupVoiceChat:
    async def leave_group_voice_chat(
            self: "rubigram.Client",
            group_guid: str,
            voice_chat_id: str,
    ) -> rubigram.types.Update:
        """
        Leave a voice chat in a group.

        Args:
        - group_guid (str): The GUID of the group.
        - voice_chat_id (str): The ID of the voice chat.

        Returns:
        - rubigram.types.Update: Update object confirming the leave voice chat action.
        """
        return await self.builder('leaveGroupVoiceChat',
                                  input={
                                      'group_guid': group_guid,
                                      'voice_chat_id': voice_chat_id,
                                  })
