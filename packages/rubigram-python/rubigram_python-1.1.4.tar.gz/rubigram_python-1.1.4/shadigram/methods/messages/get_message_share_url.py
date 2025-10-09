import shadigram


class GetMessageShareUrl:
    async def get_message_url(
            self: "shadigram.Client",
            object_guid: str,
            message_id: str,
    ):
        input = dict(
            object_guid=object_guid,
            message_id=message_id,
        )

        return await self.builder(name='getMessageShareUrl',
                                  input=input)
