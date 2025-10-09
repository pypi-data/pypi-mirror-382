
from typing import Union
import rubigram


def get_to_dict(obj):
    if hasattr(obj, 'to_dict'):
        if callable(obj.to_dict):
            return obj.to_dict()
        elif isinstance(obj.to_dict, dict):
            return obj.to_dict
    return {}


class CopyMessages:
    async def copy_messages(
            self: "rubigram.Client",
            to_object_guid: str,
            from_object_guid: str,
            message_ids: Union[int, str, list],
            *args,
            **kwargs
    ) -> list:
        if not isinstance(message_ids, list):
            message_ids = [message_ids]

        messages = []
        for msg_id in message_ids:
            result = await self.get_messages_by_id(from_object_guid, [msg_id])
            if not result.messages:
                continue
            message = result.messages[0]

            file_inline = message.file_inline
            sticker = message.sticker
            text = message.text

            if sticker:
                sent = await self.send_message(to_object_guid, sticker=sticker.to_dict())
                messages.append(sent)
                continue
            elif file_inline:
                data = get_to_dict(file_inline)
                data.pop('file_id', None)
                kwargs.update(data)
                if file_inline.type not in ['Gif', 'Sticker']:
                    file_inline = await self.download(file_inline)
                    sent = await self.send_message(
                        object_guid=to_object_guid,
                        text=text,
                        file_inline=file_inline,
                        *args,
                        **kwargs
                    )
                    messages.append(sent)
                    continue

            sent = await self.send_message(to_object_guid, text, file_inline=file_inline, *args, **kwargs)
            messages.append(sent)

        return messages
