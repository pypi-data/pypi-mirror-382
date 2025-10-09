
import shadigram


class TerminateOtherSession:
    """
    A class to terminate a user session.

    Methods:
    - terminate_other_session: Terminates a specific user session.

    Attributes:
    - self (shadigram.Client): An instance of the shadigram client.
    """

    async def terminate_other_session(
            self: "shadigram.Client",
    ) -> shadigram.types.Update:
        """
        Terminates a user session.

        Returns:
        - shadigram.types.Update: Updated user information after terminating the session.
        """
        return await self.builder('terminateOtherSession',
                                  input={})
