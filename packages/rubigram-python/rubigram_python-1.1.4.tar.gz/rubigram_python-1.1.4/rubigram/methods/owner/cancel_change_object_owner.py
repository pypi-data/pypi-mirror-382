
import rubigram


class CancelChangeObjectOwner:
    """
    A class to handle canceling the change of an object's owner.

    Methods:
    - cancel_change_object_owner: Cancels the process of changing the object's owner.

    Attributes:
    - self (rubigram.Client): An instance of the rubigram client.
    """

    async def cancel_change_object_owner(
        self: "rubigram.Client",
        object_guid: str
    ) -> rubigram.types.Update:
        """
        Cancels the process of changing the ownership of an object.

        Parameters:
        - object_guid (str): The unique identifier of the object whose ownership change is to be canceled.

        Returns:
        - rubigram.types.Update: The updated status after canceling the ownership change.
        """
        input_data = {'object_guid': object_guid}

        return await self.builder('cancelChangeObjectOwner', input=input_data)
