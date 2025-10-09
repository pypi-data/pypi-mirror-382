from ... import exceptions

import shadigram


class Disconnect:
    async def disconnect(self: "shadigram.Client"):
        try:
            return await self.connection.close()
            self.logger.info(f'the client was disconnected')

        except AttributeError:
            raise exceptions.NoConnection(
                'You must first connect the Client'
                ' with the *.connect() method')
