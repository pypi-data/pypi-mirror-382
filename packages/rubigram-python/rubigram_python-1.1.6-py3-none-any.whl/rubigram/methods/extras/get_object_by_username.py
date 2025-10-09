
import rubigram


class GetObjectByUsername:
    async def get_object_by_username(
            self: "rubigram.Client",
            username: str,
    ) -> rubigram.types.Update:
        """
        Get an object (user, group, or channel) by its username.

        Args:
            username (str): The username of the object.

        Returns:
            rubigram.types.Update: The update containing information about the object.
        """
        username = username.replace('@', '')
        return await self.builder('getObjectByUsername',
                                  input={
                                      'username': username,
                                  })
