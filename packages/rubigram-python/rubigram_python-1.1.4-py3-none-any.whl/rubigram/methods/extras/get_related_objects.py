
import rubigram


class GetRelatedObjects:
    async def get_related_objects(
            self: "rubigram.Client",
            object_guid: str,
    ) -> rubigram.types.Update:
        """
        Get related objects for a given object.

        Args:
            object_guid (str): The GUID of the object.

        Returns:
            rubigram.types.Update: The update containing information about related objects.
        """
        return await self.builder(name='getRelatedObjects', input=dict(object_guid=object_guid))
