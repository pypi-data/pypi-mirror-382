
import rubigram


class TerminateOtherSession:
    """
    A class to terminate a user session.

    Methods:
    - terminate_other_session: Terminates a specific user session.

    Attributes:
    - self (rubigram.Client): An instance of the rubigram client.
    """

    async def terminate_other_session(
            self: "rubigram.Client",
    ) -> rubigram.types.Update:
        """
        Terminates a user session.

        Returns:
        - rubigram.types.Update: Updated user information after terminating the session.
        """
        return await self.builder('terminateOtherSession',
                                  input={})
