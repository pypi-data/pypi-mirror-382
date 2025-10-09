
import rubigram


class CheckUserUsername:
    """
    Provides a method to check the availability of a username for a user.

    Methods:
    - check_user_username: Check the availability of a username.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def check_user_username(
            self: "rubigram.Client",
            username: str) -> "rubigram.types.Update":
        """
        Check the availability of a username for a user.

        Args:
        - username (str): The username to be checked.

        Returns:
        - The result of the username availability check.
        """
        return await self.builder('checkUserUsername', input=dict(username=username))
