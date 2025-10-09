import shadigram


class SendSticker:
    async def send_sticker(
            self: "shadigram.Client",
            object_guid: str,
            emoji_character: str,
            sticker_id: str,
            sticker_set_id: str,
            file: dict,
            w_h_ratio: str = '1.0',
            reply_to_message_id: str = None,
            auto_delete: int = None,
    ):
        if not isinstance(file, dict):
            file = file.to_dict()

        data = {
            'emoji_character': emoji_character,
            'sticker_id': sticker_id,
            'sticker_set_id': sticker_set_id,
            'w_h_ratio': w_h_ratio,
            'file': file,
        }

        return await self.send_message(
            object_guid=object_guid,
            sticker=data,
            reply_to_message_id=reply_to_message_id,
            auto_delete=auto_delete,
        )
