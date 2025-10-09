
import rubigram


class UpdateUsername:
    """
    Provides a method to update the username of the user.

    Methods:
    - update_username: Update the username of the user.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def update_username(
            self: "rubigram.Client",
            username: str
    ) -> rubigram.types.Update:
        """
        Update the username of the user.

        Parameters:
        - username (str): The new username for the user.

        Returns:
        - rubigram.types.Update: The updated user information after the username update.
        """
        return await self.builder('updateUsername', input={'username': username.replace('@', '')})
