
from ... import exceptions
import rubigram


class Disconnect:
    async def disconnect(self: "rubigram.Client") -> None:
        """
        Disconnect from the Rubpy server.

        Raises:
        - exceptions.NoConnection: If the client is not connected.
        """
        try:
            await self.connection.close()
            self.logger.info('The client was disconnected')

        except AttributeError:
            raise exceptions.NoConnection(
                'You must first connect the Client'
                ' with the *.connect() method')
