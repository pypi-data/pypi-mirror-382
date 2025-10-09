
import rubigram
from rubigram.types import Update


class GetMySessions:
    """
    Provides a method to get information about the current user's sessions.

    Methods:
    - get_my_sessions: Get information about the current user's sessions.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def get_my_sessions(
            self: "rubigram.Client"
    ) -> Update:
        """
        Get information about the current user's sessions.

        Returns:
        - rubigram.types.Update: Information about the user's sessions.
        """
        return await self.builder('getMySessions')  # type: ignore
