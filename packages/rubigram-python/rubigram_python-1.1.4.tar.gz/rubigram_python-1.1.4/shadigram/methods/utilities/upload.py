import shadigram


class UploadFile:
    async def upload(self: "shadigram.Client", file, *args, **kwargs):
        return await self.connection.upload_file(file=file, *args, **kwargs)
