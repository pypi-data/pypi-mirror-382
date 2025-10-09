
from typing import Optional
import rubigram
from rubigram.types import Update


class EditChannelInfo:
    async def edit_channel_info(
        self: "rubigram.Client",
        channel_guid: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        channel_type: Optional[str] = None,
        sign_messages: Optional[str] = None,
        is_restricted_content: Optional[bool] = None,
        chat_reaction_setting: Optional[dict] = None,
        chat_history_for_new_members: Optional[str] = None,
    ) -> Update:
        """
        Edit information of a channel.

        Parameters:
        - channel_guid (str): The GUID of the channel.
        - title (str, optional): The new title of the channel.
        - description (str, optional): The new description of the channel.
        - channel_type (str, optional): The new type of the channel.
        - sign_messages (str, optional): Whether to sign messages in the channel.
        - is_restricted_content (Optional[bool]): change access restricted content for the group.
        - chat_reaction_setting (dict, optional): The new chat reaction setting.
        - chat_history_for_new_members (str, optional): The chat history visibility for new members.

        Returns:
        rubigram.types.Update: The result of the API call.
        """
        updated_parameters = []
        input_data = {
            'channel_guid': channel_guid,
        }

        if title is not None:
            input_data['title'] = title
            updated_parameters.append('title')

        if description is not None:
            input_data['description'] = description
            updated_parameters.append('description')

        if channel_type is not None:
            input_data['channel_type'] = channel_type
            updated_parameters.append('channel_type')

        if sign_messages is not None:
            input_data['sign_messages'] = sign_messages
            updated_parameters.append('sign_messages')

        if is_restricted_content is not None:
            input_data['is_restricted_content'] = is_restricted_content
            updated_parameters.append('is_restricted_content')

        if chat_reaction_setting is not None:
            input_data['chat_reaction_setting'] = chat_reaction_setting
            updated_parameters.append('chat_reaction_setting')

        if chat_history_for_new_members is not None:
            if chat_history_for_new_members not in ('Hidden', 'Visible'):
                raise ValueError(
                    '`chat_history_for_new_members` argument can only be in `["Hidden", "Visible"]`.')
            input_data['chat_history_for_new_members'] = chat_history_for_new_members
            updated_parameters.append('chat_history_for_new_members')

        input_data['updated_parameters'] = updated_parameters
        return await self.builder('editChannelInfo', input=input_data)
