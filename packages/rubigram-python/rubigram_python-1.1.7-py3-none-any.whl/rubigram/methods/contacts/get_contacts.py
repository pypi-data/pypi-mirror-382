
import rubigram
from typing import Optional, Union


class GetContacts:
    async def get_contacts(
            self: "rubigram.Client",
            start_id: Optional[Union[str, int]] = None,
    ) -> rubigram.types.Update:
        """
        Get a list of contacts.

        Args:
            self ("rubigram.Client"): The rubigram client.
            start_id (Optional[Union[str, int]], optional): Start ID for pagination. Defaults to None.

        Returns:
            rubigram.types.Update: The result of the API call.
        """
        return self.builder(
            name='getContacts', input={
                'start_id': str(start_id)})
