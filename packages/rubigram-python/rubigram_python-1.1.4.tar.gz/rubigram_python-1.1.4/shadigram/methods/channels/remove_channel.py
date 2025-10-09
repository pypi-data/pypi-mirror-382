import shadigram


class RemoveChannel:
    async def remove_channel(
            self: "shadigram.Client",
            channel_guid: str,
    ):
        return await self.builder('removeChannel',
                                  input={
                                      'channel_guid': channel_guid,
                                  })
