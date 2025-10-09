
import rubigram


class GetGroupOnlineCount:
    async def get_group_online_count(
            self: "rubigram.Client",
            group_guid: str
    ) -> rubigram.types.Update:
        """
        Retrieve the count of online members in a group.

        Args:
        - group_guid (str): The group identifier.

        Returns:
        - rubigram.types.Update: The result of the API request.
        """
        input_data = {
            'group_guid': group_guid
        }

        return await self.builder('getGroupOnlineCount', input=input_data)
