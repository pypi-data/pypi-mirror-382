
from time import time
from typing import Optional, Union
import rubigram


class GetContactsUpdates:
    async def get_contacts_updates(
            self: "rubigram.Client",
            state: Optional[Union[str, int]] = round(time()) - 150,
    ) -> rubigram.types.Update:
        """
        Get updates related to contacts.

        Args:
            self (rubigram.Client): The rubigram client.
            state (Optional[Union[str, int]], optional):
                The state parameter to filter updates. Defaults to `round(time()) - 150`.

        Returns:
            rubigram.types.Update: The update related to contacts.
        """
        return await self.builder(name='getContactsUpdates',
                                  input={'state': int(state)})
