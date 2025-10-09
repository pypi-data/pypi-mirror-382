
from typing import Optional, Union
from pathlib import Path
import rubigram


class SendDocument:
    """
    Provides a method to send a document.

    Methods:
    - send_document: Send a document.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def send_document(
        self: "rubigram.Client",
        object_guid: str,
        document: Union[Path, bytes],
        caption: Optional[str] = None,
        reply_to_message_id: Optional[str] = None,
        auto_delete: Optional[int] = None,
        progress: bool = False,
        *args, **kwargs,
    ) -> rubigram.types.Update:
        """
        Send a document.

        Parameters:
        - object_guid (str): The GUID of the recipient.
        - document (Union[Path, bytes]): The document data.
        - caption (Optional[str]): The caption for the document. Defaults to None.
        - reply_to_message_id (Optional[str]): The ID of the message to which this is a reply. Defaults to None.
        - auto_delete (Optional[int]): Auto-delete duration in seconds. Defaults to None.
        - progress: Optional message object for showing upload progress.
                    If None, only terminal progress will be shown.

        Returns:
        - rubigram.types.Update: The update indicating the success of the document sending.
        """
        return await self.send_message(
            object_guid=object_guid,
            text=caption,
            reply_to_message_id=reply_to_message_id,
            file_inline=document,
            thumb=False,
            auto_delete=auto_delete,
            progress=progress,
            *args,
            **kwargs,
        )
