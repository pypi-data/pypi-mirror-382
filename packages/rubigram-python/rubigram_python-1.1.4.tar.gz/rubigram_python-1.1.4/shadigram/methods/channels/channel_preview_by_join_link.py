import shadigram


class ChannelPreviewByJoinLink:
    async def channel_preview_by_join_link(
            self: "shadigram.Client",
            link: str,
    ):
        if '/' in link:
            link = link.split('/')[-1]

        return await self.builder('channelPreviewByJoinLink',
                                  input={
                                      'hash_link': link,
                                  })
