
import rubigram
from rubigram.types import Update


class GetBlockedUsers:
    """
    Provides a method to get a list of blocked users.

    Methods:
    - get_blocked_users: Get a list of blocked users.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def get_blocked_users(
            self: "rubigram.Client"
    ) -> Update:
        """
        Get a list of blocked users.

        Returns:
        - rubigram.types.Update: List of blocked users.
        """
        return await self.builder('getBlockedUsers')  # type: ignore
