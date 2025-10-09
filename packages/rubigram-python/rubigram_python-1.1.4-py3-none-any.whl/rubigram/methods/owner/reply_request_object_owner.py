
import rubigram
from rubigram.types import Update


class ReplyRequestObjectOwner:
    async def reply_request_object_owner(
        self: "rubigram.Client",
        object_guid: str,
        action: str = "Accept"
    ) -> Update:
        """
        Accept or reject an ownership transfer request for a group or channel.

        Parameters:
        - object_guid (str): The unique identifier of the group or channel.
        - action (str): The action to be performed. It can be "Accept" or "Reject".

        Returns:
        - rubigram.types.Update: The result of the request.
        """
        if action not in ["Accept", "Reject"]:
            raise ValueError(
                '`action` argument can only be in ["Accept", "Reject"].')

        input_data = {'object_guid': object_guid, 'action': action}
        return await self.builder('replyRequestObjectOwner', input=input_data)
