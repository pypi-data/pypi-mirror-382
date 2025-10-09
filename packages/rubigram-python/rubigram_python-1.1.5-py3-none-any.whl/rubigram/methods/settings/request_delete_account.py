
import rubigram


class RequestDeleteAccount:
    """
    Provides a method to request the deletion of a user's account.

    Methods:
    - request_delete_account: Sends a request to delete the user's account.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def request_delete_account(
            self: "rubigram.Client"
    ) -> "rubigram.types.Update":
        """
        Sends a request to delete the user's account.

        Returns:
        - rubigram.types.Update: The result of the delete request.
        """
        return await self.builder('requestDeleteAccount')
