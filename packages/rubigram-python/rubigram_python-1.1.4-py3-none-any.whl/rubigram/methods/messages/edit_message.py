
from typing import Union
import rubigram


class EditMessage:
    """
    Provides a method to edit a message.

    Methods:
    - edit_message: Edit the specified message associated with the given object.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def edit_message(
        self: "rubigram.Client",
        object_guid: str,
        message_id: Union[int, str],
        text: str,
        parse_mode: str = None,
    ) -> rubigram.types.Update:
        """
        Edit the specified message associated with the given object.

        Parameters:
        - object_guid (str): The GUID of the object associated with the message (e.g., user, group, channel).
        - message_id (Union[int, str]): The ID of the message to be edited.
        - text (str): The new text content for the message.
        - parse_mode (str): The parse mode for the text, can be 'markdown' or 'html'. Defaults to None.

        Returns:
        - rubigram.types.Update: The updated information after editing the message.
        """
        parse_mode = parse_mode or self.parse_mode
        input_data = {
            'object_guid': object_guid,
            'message_id': str(message_id),
            'text': text.strip(),
        }

        if isinstance(parse_mode, str):
            markdown = (
                self.markdown.to_metadata(self.markdown.to_markdown(text))
                if parse_mode == 'html'
                else self.markdown.to_metadata(text)
            )
            input_data.update(markdown)

        return await self.builder(name='editMessage', input=input_data)
