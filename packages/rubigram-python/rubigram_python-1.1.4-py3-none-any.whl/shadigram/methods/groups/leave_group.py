import shadigram


class LeaveGroup:
    async def leave_group(
            self: "shadigram.Client",
            group_guid: str,
    ):
        return await self.builder('leaveGroup', input=dict(group_guid=group_guid))
