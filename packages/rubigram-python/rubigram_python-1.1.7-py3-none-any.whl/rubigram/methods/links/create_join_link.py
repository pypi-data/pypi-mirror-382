
import rubigram
from typing import Optional


class CreateJoinLink:
    async def create_join_link(
            self: "rubigram.Client",
            object_guid: str,
            expire_time: Optional[int] = None,
            request_needed: bool = False,
            title: Optional[str] = None,
            usage_limit: int = 0
    ) -> rubigram.types.Update:
        """
        Create a join link for a group or channel.

        Args:
        - object_guid (str): The GUID of the group or channel.
        - expire_time (Optional[int]): Expiration time for the link (optional).
        - request_needed (bool): Whether join requests need approval (default is False).
        - title (Optional[str]): Title of the join link (optional).
        - usage_limit (int): The maximum number of times the link can be used (default is 0 for unlimited).

        Returns:
        - rubigram.types.Update: The result of the API call.

        Raises:
        - ValueError: If `request_needed` is not a boolean.
        """
        if not isinstance(request_needed, bool):
            raise ValueError("`request_needed` must be of boolean type only.")

        input_data = {
            'object_guid': object_guid,
            'request_needed': request_needed,
            'usage_limit': usage_limit
        }

        if isinstance(expire_time, int):
            input_data['expire_time'] = expire_time

        if isinstance(title, str):
            input_data['title'] = title

        return await self.builder('createJoinLink', input=input_data)
