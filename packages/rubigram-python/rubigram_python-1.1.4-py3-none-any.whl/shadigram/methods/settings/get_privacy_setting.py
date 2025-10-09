import shadigram


class GetPrivacySetting:
    async def get_privacy_setting(self: "shadigram.Client"):
        return await self.builder('getPrivacySetting')
