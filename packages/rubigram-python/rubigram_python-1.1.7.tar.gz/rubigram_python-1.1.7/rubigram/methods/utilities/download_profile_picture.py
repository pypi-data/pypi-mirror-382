
from typing import Literal, Optional
import rubigram
import aiofiles
import os


class DownloadProfilePicture:

    async def download_profile_picture(
            self: "rubigram.Client",
            object_guid: str,
            action: Literal["All", "One"],
            save: Optional[str] = None
    ) -> str:
        """
        Download and optionally save profile pictures.

        Args:
            object_guid (str): The GUID of the user, group, or channel.
            action (Literal["All", "One"]): Determines whether to download one or all profile pictures.
            save (Optional[str]): The filename for saving images. If None, images are not saved.

        Returns:
            str: A message indicating the download and save status.
        """
        avatars = await self.get_avatars(object_guid)

        if not avatars or not avatars.avatars:
            return "No profile pictures found."

        if action == "One":
            avatar = avatars.avatars[0].main
            filename = self._generate_filename(save, 1) if save else None
            return await self._download_and_save(avatar, filename)

        messages = []
        for index, avatar in enumerate(avatars.avatars, start=1):
            filename = self._generate_filename(save, index) if save else None
            messages.append(await self._download_and_save(avatar, filename))

        return "\n".join(messages)

    async def _download_and_save(self, avatar, filename: Optional[str]) -> str:
        """
        Download an avatar and optionally save it to a file.

        Args:
            avatar: The avatar object containing file details.
            filename (Optional[str]): The filename to save the image. If None, the file is not saved.

        Returns:
            str: A message indicating the save status.
        """
        async with self.connection.session.get(
            url=f'https://messenger{avatar.dc_id}.iranlms.ir/InternFile.ashx',
            params={'id': avatar.file_id, 'ach': avatar.access_hash_rec},
        ) as response:
            if response.ok:
                data = await response.read()
                if filename:
                    async with aiofiles.open(filename, "wb") as f:
                        await f.write(data)
                    return f"Saved: {filename}"
                return "Downloaded but not saved."
        return "Download failed."

    def _generate_filename(self, base_name: str, index: int) -> str:
        """
        Generate a filename with an index if multiple images are saved.

        Args:
            base_name (str): The base name of the file.
            index (int): The index number for multiple images.

        Returns:
            str: The formatted filename.
        """
        name, ext = os.path.splitext(base_name)
        return f"{name}({index}){ext}"
