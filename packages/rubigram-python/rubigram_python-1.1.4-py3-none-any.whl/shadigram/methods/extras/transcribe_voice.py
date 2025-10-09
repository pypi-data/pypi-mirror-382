import shadigram


class TranscribeVoice:
    async def transcribe_voice(
            self: "shadigram.Client",
            object_guid: str,
            message_id: str,
    ):
        return await self.builder(
            name='transcribeVoice',
            input=dict(object_guid=object_guid, message_id=message_id)
        )
