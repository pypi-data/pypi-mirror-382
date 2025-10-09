import shadigram

from pathlib import Path
from typing import Union


class UploadAvatar:
    async def upload_avatar(
            self: "shadigram.Client",
            object_guid: str,
            image: Union[Path, bytes], *args, **kwargs,
    ):
        if object_guid.lower() in ('me', 'cloud', 'self'):
            object_guid = self.guid

        if isinstance(image, str):
            kwargs['file_name'] = kwargs.get('file_name', image.split('/')[-1])
        else:
            kwargs['file_name'] = kwargs.get('file_name', 'shadigram.jpg')

        upload = await self.upload(image, *args, **kwargs)

        input = dict(
            object_guid=object_guid,
            thumbnail_file_id=upload.file_id,
            main_file_id=upload.file_id,
        )

        return await self.builder(name='uploadAvatar', input=input)
