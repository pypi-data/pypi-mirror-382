from typing import Union

import balethon


class RestrictChatMember:

    async def restrict_chat_member(
            self: "balethon.Client",
            chat_id: Union[int, str],
            user_id: Union[int, str]
    ) -> bool:
        chat_id = await self.resolve_peer_id(chat_id)
        user_id = await self.resolve_peer_id(user_id)
        return await self.auto_execute("post", "restrictChatMember", locals())
