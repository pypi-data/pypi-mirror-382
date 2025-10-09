import shadigram


class UserIsAdmin:
    async def user_is_admin(
            self: "shadigram.Client",
            object_guid: str,
            user_guid: str,
    ) -> bool:
        has_continue = True
        next_start_id = None

        while has_continue:
            result = await self.get_group_admin_members(object_guid,
                                                        next_start_id) if object_guid.startswith('g0') else await self.get_channel_admin_members(object_guid,
                                                                                                                                                 next_start_id)
            has_continue = result.has_continue
            next_start_id = result.next_start_id

            for user in result.in_chat_members:
                if user_guid == user.member_guid:
                    return True

        return False
