
import rubigram


class GetReadParticipants:
    async def get_read_participants(
            self: "rubigram.Client",
            group_guid: str,
            message_id: str
    ) -> rubigram.types.Update:
        """
        Retrieve the list of participants who have read a message.

        Args:
        - group_guid (str): The group identifier.
        - message_id (str): The message identifier.

        Returns:
        - rubigram.types.Update: The result of the API request.
        """
        input_data = {
            'group_guid': group_guid,
            'message_id': message_id
        }

        return await self.builder('getGroupMessageReadParticipants', input=input_data)
