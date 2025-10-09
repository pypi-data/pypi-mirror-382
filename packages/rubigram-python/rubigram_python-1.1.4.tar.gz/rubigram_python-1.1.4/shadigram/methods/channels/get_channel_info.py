import shadigram


class GetChannelInfo:
    async def get_channel_info(
            self: "shadigram.Client",
            channel_guid: str,
    ):
        return await self.builder('getChannelInfo',
                                  input={
                                      'channel_guid': channel_guid,
                                  })
