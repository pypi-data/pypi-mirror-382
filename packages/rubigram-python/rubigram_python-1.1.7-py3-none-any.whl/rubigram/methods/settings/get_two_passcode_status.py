
import rubigram
from rubigram.types import Update


class GetTwoPasscodeStatus:
    """
    Provides a method to get the two-passcode status for the user.

    Methods:
    - get_two_passcode_status: Get the two-passcode status for the user.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def get_two_passcode_status(
            self: "rubigram.Client"
    ) -> Update:
        """
        Get the two-passcode status for the user.

        Returns:
        - rubigram.types.Update: The two-passcode status for the user.
        """
        return await self.builder('getTwoPasscodeStatus')  # type: ignore
