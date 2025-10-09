import shadigram
import aiofiles


class Download:
    async def download(
            self: "shadigram.Client",
            file_inline: "shadigram.types.Results",
            save_as: str = None,
            chunk_size: int = 131072,
            callback=None,
            *args,
            **kwargs):
        if isinstance(file_inline, dict):
            file_inline = shadigram.types.Results(file_inline)

        result = await self.connection.download(
            file_inline.dc_id,
            file_inline.file_id,
            file_inline.access_hash_rec,
            file_inline.size,
            chunk=chunk_size,
            callback=callback,
        )

        if isinstance(save_as, str):
            if '.' not in save_as:
                save_as = ''.join([save_as, '.', file_inline.mime])

            async with aiofiles.open(save_as, 'wb+') as file:
                await file.write(result)

        return result
