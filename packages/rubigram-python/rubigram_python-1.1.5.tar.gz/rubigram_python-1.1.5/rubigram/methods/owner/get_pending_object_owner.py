
import rubigram


class GetPendingObjectOwner:
    """
    A class to retrieve the pending owner of an object.

    Methods:
    - get_pending_object_owner: Retrieves the pending ownership status of an object.

    Attributes:
    - self (rubigram.Client): An instance of the rubigram client.
    """

    async def get_pending_object_owner(
        self: "rubigram.Client",
        object_guid: str
    ) -> rubigram.types.Update:
        """
        Retrieves the pending owner information for an object.

        Parameters:
        - object_guid (str): The unique identifier of the object whose pending ownership is to be retrieved.

        Returns:
        - rubigram.types.Update: The updated information about the pending ownership of the object.
        """
        input_data = {'object_guid': object_guid}

        return await self.builder('getPendingObjectOwner', input=input_data)
