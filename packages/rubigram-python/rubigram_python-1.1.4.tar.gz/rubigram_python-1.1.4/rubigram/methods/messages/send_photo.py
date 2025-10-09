
from typing import Union, Optional
from pathlib import Path
import rubigram


class SendPhoto:
    async def send_photo(
            self: "rubigram.Client",
            object_guid: str,
            photo: Union[Path, bytes],
            caption: Optional[str] = None,
            reply_to_message_id: Optional[str] = None,
            is_spoil: bool = False,
            auto_delete: Optional[int] = None,
            progress: bool = False,
            *args, **kwargs,
    ) -> rubigram.types.Update:
        """
        Send a photo.

        Args:
            object_guid (str):
                The GUID of the recipient.

            photo (Path, bytes):
                The photo data.

            caption (str, optional):
                The caption for the photo. Defaults to None.

            reply_to_message_id (str, optional):
                The ID of the message to which this is a reply. Defaults to None.

            is_spoil (bool, optional):
                Whether the photo should be marked as a spoiler. Defaults to False.

            auto_delete (int, optional):
                Auto-delete duration in seconds. Defaults to None.
        """

        return await self.send_message(
            object_guid=object_guid,
            text=caption,
            reply_to_message_id=reply_to_message_id,
            file_inline=photo,
            is_spoil=is_spoil,
            type='Image',
            auto_delete=auto_delete,
            progress=progress,
            *args, **kwargs
        )
