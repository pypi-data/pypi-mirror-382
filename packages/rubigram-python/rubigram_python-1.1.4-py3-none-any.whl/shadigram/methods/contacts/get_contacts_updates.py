from time import time
from typing import Optional, Union
import shadigram


class GetContactsUpdates:
    async def get_contacts_updates(
            self: "shadigram.Client",
            state: Optional[Union[str, int]] = round(time()) - 150,
    ):
        return await self.builder(name='getContactsUpdates',
                                  input={'state': int(state)})
