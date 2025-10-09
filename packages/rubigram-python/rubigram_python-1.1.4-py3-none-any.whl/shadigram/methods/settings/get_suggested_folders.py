import shadigram


class GetSuggestedFolders:
    async def get_suggested_folders(self: "shadigram.Client"):
        return await self.builder('getSuggestedFolders')
