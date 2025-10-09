import shadigram


class GroupPreviewByJoinLink:
    async def group_preview_by_join_link(
            self: "shadigram.Client",
            link: str,
    ):
        if '/' in link:
            link = link.split('/')[-1]

        return await self.builder('groupPreviewByJoinLink',
                                  input={
                                      'hash_link': link,
                                  })
