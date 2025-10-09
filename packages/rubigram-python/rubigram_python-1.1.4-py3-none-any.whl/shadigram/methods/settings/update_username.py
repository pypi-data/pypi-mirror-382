import shadigram


class UpdateUsername:
    async def update_username(self: "shadigram.Client", username: str):
        return await self.builder('updateUsername', input={'username': username.replace('@', '')})
