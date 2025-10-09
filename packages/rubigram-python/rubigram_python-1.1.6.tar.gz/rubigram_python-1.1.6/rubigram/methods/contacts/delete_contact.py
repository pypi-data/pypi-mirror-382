
import rubigram


class DeleteContact:
    async def delete_contact(
            self: "rubigram.Client",
            user_guid: str,
    ) -> rubigram.types.Update:
        """
        Deletes a contact from the client's address book.

        Args:
            user_guid (str): The GUID (Globally Unique Identifier) of the contact to be deleted.

        Returns:
            rubigram.types.Update: The result of the contact deletion operation.

        Raises:
            Any exceptions that might occur during the contact deletion process.

        Note:
            - The `user_guid` parameter should be the GUID of the contact to be deleted.
        """
        return self.builder(
            name='deleteContact', input={
                'user_guid': user_guid})
