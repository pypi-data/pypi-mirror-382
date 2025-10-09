
import rubigram


class SendChatActivity:
    async def send_chat_activity(
            self: "rubigram.Client",
            object_guid: str,
            activity: str = 'Typing',
    ) -> rubigram.types.Update:
        """
        Sends a chat activity, such as typing, uploading, or recording.

        Args:
            object_guid (str): The GUID of the chat.
            activity (str, optional): The type of activity. Defaults to 'Typing'.

        Returns:
            rubigram.types.Update: The result of the operation.

        Raises:
            ValueError: If the `activity` argument is not one of `["Typing", "Uploading", "Recording"]`.
        """
        if activity not in ('Typing', 'Uploading', 'Recording'):
            raise ValueError(
                '`activity` argument can only be in `["Typing", "Uploading", "Recording"]`')

        return await self.builder('sendChatActivity',
                                  input={
                                      'object_guid': object_guid,
                                      'activity': activity,
                                  })
