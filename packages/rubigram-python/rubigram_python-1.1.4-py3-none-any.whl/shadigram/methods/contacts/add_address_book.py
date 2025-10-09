import shadigram


class AddAddressBook:
    async def add_address_book(
            self: "shadigram.Client",
            phone: str,
            first_name: str,
            last_name: str = '',
    ):
        input = {
            'phone': phone,
            'first_name': str(first_name),
            'last_name': str(last_name),
        }

        return await self.builder(name='addAddressBook',
                                  input=input)
