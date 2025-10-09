import shadigram


class DiscardgroupVoiceChat:
    async def discard_group_voice_chat(
            self: "shadigram.Client",
            group_guid: str,
            voice_chat_id: str,
    ):
        return await self.builder(name='discardgroupVoiceChat',
                                  input={
                                      'group_guid': group_guid,
                                      'voice_chat_id': voice_chat_id,
                                  })
