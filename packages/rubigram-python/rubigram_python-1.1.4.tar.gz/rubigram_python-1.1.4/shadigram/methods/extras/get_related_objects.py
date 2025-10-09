import shadigram


class GetRelatedObjects:
    async def get_related_objects(
            self: "shadigram.Client",
            object_guid: str,
    ):
        return await self.builder(
            name='getRelatedObjects',
            input=dict(object_guid=object_guid),
        )
