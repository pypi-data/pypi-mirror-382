import shadigram


class DeleteContact:
    async def delete_contact(
            self: "shadigram.Client",
            user_guid: str,
    ):
        return self.builder(name='deleteContact',
                            input={'user_guid': user_guid})
