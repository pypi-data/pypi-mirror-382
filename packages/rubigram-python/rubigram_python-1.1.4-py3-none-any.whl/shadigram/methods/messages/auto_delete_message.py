import shadigram
import asyncio


class AutoDeleteMessage:
    async def auto_delete_message(
            self: "shadigram.Client",
            object_guid: str,
            message_id: str,
            time: int,
    ):
        await asyncio.sleep(time)
        return await self.delete_messages(object_guid, message_id)
