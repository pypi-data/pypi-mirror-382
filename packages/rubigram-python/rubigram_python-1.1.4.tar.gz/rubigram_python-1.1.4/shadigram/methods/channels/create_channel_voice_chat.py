import shadigram


class CreateChannelVoiceChat:
    async def create_channel_voice_chat(
            self: "shadigram.Client",
            channel_guid: str,
    ):
        return await self.builder('createChannelVoiceChat',
                                  input={
                                      'channel_guid': channel_guid,
                                  })
