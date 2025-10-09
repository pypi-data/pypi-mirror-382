
import rubigram


class AddAddressBook:
    async def add_address_book(
            self: "rubigram.Client",
            phone: str,
            first_name: str,
            last_name: str = '',
    ) -> rubigram.types.Update:
        """
        Adds a contact to the client's address book.

        Args:
            phone (str): The phone number of the contact to be added.
            first_name (str): The first name of the contact.
            last_name (str, optional): The last name of the contact. Defaults to an empty string.

        Returns:
            rubigram.types.Update: The result of the address book addition operation.

        Raises:
            Any exceptions that might occur during the address book addition process.

        Note:
            - The `phone` parameter should be a valid phone number.
            - The `first_name` and `last_name` parameters represent the name of the contact.
              If the contact has no last name, `last_name` can be an empty string.
        """
        input = {
            'phone': phone,
            'first_name': str(first_name),
            'last_name': str(last_name),
        }

        return await self.builder(name='addAddressBook', input=input)
