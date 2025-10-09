import shadigram


class GetTwoPasscodeStatus:
    async def get_two_passcode_status(self: "shadigram.Client"):
        return await self.builder('getTwoPasscodeStatus')
