import shadigram


class GetPollStatus:
    async def get_poll_status(
            self: "shadigram.Client",
            poll_id: str,
    ):
        return self.builder(name='getPollStatus',
                            input={
                                'poll_id': poll_id,
                            })
