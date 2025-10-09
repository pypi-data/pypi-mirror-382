
import shadigram


class RequestDeleteAccount:
    """
    Provides a method to request the deletion of a user's account.

    Methods:
    - request_delete_account: Sends a request to delete the user's account.

    Attributes:
    - self (shadigram.Client): The shadigram client instance.
    """

    async def request_delete_account(
            self: "shadigram.Client"
    ) -> "shadigram.types.Update":
        """
        Sends a request to delete the user's account.

        Returns:
        - shadigram.types.Update: The result of the delete request.
        """
        return await self.builder('requestDeleteAccount')
