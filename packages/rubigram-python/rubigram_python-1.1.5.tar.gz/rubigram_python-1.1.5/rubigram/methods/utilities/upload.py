
import rubigram
from .progress import Progress


class UploadFile:
    """
    Provides a method to upload a file.

    Methods:
    - upload: Upload a file.

    Attributes:
    - self (rubigram.Client): The rubigram client instance.
    """

    async def upload(
        self: "rubigram.Client",
        file,
        *args,
        client=None,
        object_guid=None,
        **kwargs
    ) -> "rubigram.types.Update":
        """
        Upload a file.

        Args:
        - file: The file to be uploaded.
        - *args: Additional positional arguments.
        - client: Optional rubigram.Client instance for message updates.
        - message: Optional message object for editing during upload.
        - **kwargs: Additional keyword arguments.

        Returns:
        - The result of the file upload operation.
        """
        progress = Progress(client=client, object_guid=object_guid)
        if client and object_guid:
            await progress.setup()
        return await self.connection.upload_file(
            file=file,
            callback=progress,
            *args,
            **kwargs
        )
