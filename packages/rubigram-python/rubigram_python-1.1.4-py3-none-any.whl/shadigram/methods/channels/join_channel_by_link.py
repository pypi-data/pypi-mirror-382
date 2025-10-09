import shadigram


class JoinChannelByLink:
    async def join_channel_by_link(
            self: "shadigram.Client",
            link: str,
    ):
        if '/' in link:
            link = link.split('/')[-1]

        return await self.builder('joinChannelByLink',
                                  input={'hash_link': link})
