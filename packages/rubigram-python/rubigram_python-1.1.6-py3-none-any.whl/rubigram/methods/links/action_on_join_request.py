
import rubigram
from typing import Literal


class ActionOnJoinRequest:
    async def action_on_join_request(
            self: "rubigram.Client",
            object_guid: str,
            user_guid: str,
            action: Literal['Accept', 'Reject'] = 'Accept'
    ) -> rubigram.types.Update:
        """
        Perform an action on a join request.

        Args:
        - object_guid (str): The GUID of the group or channel.
        - user_guid (str): The GUID of the user requesting to join.
        - action (Literal['Accept', 'Reject']): The action to perform (default is 'Accept').

        Returns:
        - rubigram.types.Update: The result of the API call.

        Raises:
        - ValueError: If the action is not 'Accept' or 'Reject'.
        """
        if action not in ('Accept', 'Reject'):
            raise ValueError("`action` can only be 'Accept' or 'Reject'.")

        input_data = {
            'object_guid': object_guid, 'object_type': 'Group'
            if object_guid.startswith('g0') else 'Channel',
            'user_guid': user_guid, 'action': action, }

        return await self.builder('actionOnJoinRequest', input=input_data)
