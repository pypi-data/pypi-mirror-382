
import rubigram


class Join:
    async def join_chat(
            self: "rubigram.Client",
            chat: str,
    ) -> rubigram.types.Update:
        """
        Join a chat using its identifier or link.

        Args:
            chat (str): The identifier or link of the chat.

        Returns:
            rubigram.types.Update: The update containing information about the joined chat.
        """
        if chat.startswith('c0'):
            return await self.join_channel_action(chat, 'Join')
        else:
            if '@' not in chat:
                return await self.join_group(chat)
            else:
                return await self.join_channel_by_link(chat)
