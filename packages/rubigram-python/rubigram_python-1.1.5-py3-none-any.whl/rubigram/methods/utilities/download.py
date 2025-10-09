
import rubigram
import aiofiles


class Download:
    async def download(
            self: "rubigram.Client",
            file_inline: "rubigram.types.Update",
            save_as: str = None,
            chunk_size: int = 1054768,
            callback=None,
            *args,
            **kwargs,
    ) -> bytes:
        """
        Download a file using its file_inline information.

        Args:
        - file_inline (rubigram.types.Results): The file information used for downloading.
        - save_as (str, optional): The path to save the downloaded file. If None, the file will not be saved.
        - chunk_size (int, optional): The size of each chunk to download.
        - callback (callable, optional): A callback function to monitor the download progress.
        - *args, **kwargs: Additional parameters to pass to the download method.

        Returns:
        - bytes: The binary data of the downloaded file.

        Raises:
        - aiofiles.errors.OSFError: If there is an issue with file I/O (when saving the file).
        """
        if isinstance(file_inline, dict):
            file_inline = rubigram.types.Update(file_inline)

        result = await self.connection.download(
            file_inline.dc_id,
            file_inline.file_id,
            file_inline.access_hash_rec,
            file_inline.size,
            chunk=chunk_size,
            callback=callback,
            *args,
            **kwargs,
        )

        if isinstance(save_as, str):
            if '.' not in save_as:
                save_as = ''.join([save_as, '.', file_inline.mime])

            async with aiofiles.open(save_as, 'wb+') as file:
                await file.write(result)

        return result
