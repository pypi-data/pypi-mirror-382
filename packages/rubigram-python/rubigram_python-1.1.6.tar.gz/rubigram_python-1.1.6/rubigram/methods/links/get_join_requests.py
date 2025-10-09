
import rubigram


class GetJoinRequests:
    async def get_join_requests(
            self: "rubigram.Client",
            object_guid: str
    ) -> rubigram.types.Update:
        """
        Retrieve join requests for a group or channel.

        Args:
        - object_guid (str): The GUID of the group or channel.

        Returns:
        - rubigram.types.Update: The result of the API call.
        """
        input_data = {'object_guid': object_guid}
        return await self.builder('getJoinRequests', input=input_data)
