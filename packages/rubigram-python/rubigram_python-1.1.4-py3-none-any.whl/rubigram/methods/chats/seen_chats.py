
import rubigram


class SeenChats:
    async def seen_chats(
            self: "rubigram.Client",
            seen_list: dict,
    ) -> rubigram.types.Update:
        """
        Marks multiple chats as seen.

        Args:
            seen_list (dict): A dictionary containing chat GUIDs and their last seen message IDs.

        Returns:
            rubigram.types.Update: The result of the operation.
        """
        return await self.builder('seenChats',
                                  input={
                                      'seen_list': seen_list,
                                  })
