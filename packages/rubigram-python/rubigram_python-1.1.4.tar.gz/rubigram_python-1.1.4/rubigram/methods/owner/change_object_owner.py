
import rubigram
from rubigram.types import Update


class ChangeObjectOwner:
    async def add_channel(
        self: "rubigram.Client",
        object_guid: str,
        new_owner_user_guid: str,
    ) -> Update:
        """
        Change the ownership of a group or channel to a new user.

        Parameters:
        - object_guid (str): The unique identifier of the group or channel whose ownership is to be changed.
        - new_owner_user_guid (str): The unique identifier of the user who will become the new owner.

        Returns:
        - rubigram.types.Update: The result of the ownership change request.
        """
        input_data = {'object_guid': object_guid,
                      'new_owner_user_guid': new_owner_user_guid}
        return await self.builder('requestChangeObjectOwner', input=input_data)
