
import rubigram
from rubigram.types import Update


class GetPrivacySetting:
    """
    Provides a method to get the current user's privacy setting.

    Methods:
    - get_privacy_setting: Get the current user's privacy setting.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def get_privacy_setting(
            self: "rubigram.Client"
    ) -> Update:
        """
        Get the current user's privacy setting.

        Returns:
        - rubigram.types.Update: The current user's privacy setting.
        """
        return await self.builder('getPrivacySetting')  # type: ignore
