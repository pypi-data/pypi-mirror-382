import shadigram


class CheckChannelUsername:
    async def check_channel_username(
            self: "shadigram.Client",
            username: str,
    ):
        return await self.builder(
            name='checkChannelUsername',
            input={'username': username.replace('@', '')}
        )
