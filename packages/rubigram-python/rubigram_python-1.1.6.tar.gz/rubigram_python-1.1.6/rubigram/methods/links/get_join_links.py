
import rubigram
from typing import Union


class GetJoinLinks:
    async def get_join_links(
            self: "rubigram.Client",
            object_guid: str
    ) -> rubigram.types.Update:
        """
        Get join links for a group or channel.

        Args:
        - object_guid (str): The GUID of the group or channel.

        Returns:
        - rumax.types.Update: The result of the API call.
        """
        input_data = {'object_guid': object_guid}
        return await self.builder('getJoinLinks', input=input_data)
