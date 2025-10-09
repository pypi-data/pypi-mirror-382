import shadigram


class Join:
    async def join_chat(
            self: "shadigram.Client",
            chat: str,
    ):
        if chat.startswith('c0'):
            return await self.join_channel_action(chat, 'Join')
        else:
            if '@' not in chat:
                return await self.join_group(chat)
            else:
                return await self.join_channel_by_link(chat)
