import shadigram


class GetProfileLinkItems:
    async def get_profile_link_items(
            self: "shadigram.Client",
            object_guid: str,
    ):
        return await self.builder('getProfileLinkItems', input=dict(object_guid=object_guid))
