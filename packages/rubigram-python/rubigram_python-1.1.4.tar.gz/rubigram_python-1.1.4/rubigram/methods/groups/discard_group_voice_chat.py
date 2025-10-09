
import rubigram
from rubigram.types import Update


class DiscardGroupVoiceChat:
    async def discard_group_voice_chat(
        self: "rubigram.Client",
        group_guid: str,
        voice_chat_id: str,
    ) -> Update:
        """
        Discard a voice chat in a group.

        Parameters:
        - group_guid (str): The GUID of the group.
        - voice_chat_id (str): The ID of the voice chat to discard.

        Returns:
        rubigram.types.Update: The result of the API call.
        """
        return await self.builder(
            name='discardGroupVoiceChat',
            input={
                'group_guid': group_guid,
                'voice_chat_id': voice_chat_id,
            }
        )
