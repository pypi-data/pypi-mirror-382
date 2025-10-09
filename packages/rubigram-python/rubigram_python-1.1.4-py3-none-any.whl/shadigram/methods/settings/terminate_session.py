import shadigram


class TerminateSession:
    async def terminate_session(self: "shadigram.Client",
                                session_key: str,
                                ):
        return await self.builder('terminateSession',
                                  input={'session_key': session_key})
