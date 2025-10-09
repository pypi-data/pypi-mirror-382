from typing import Union

import balethon


class LeaveChat:

    async def leave_chat(
            self: "balethon.Client",
            chat_id: Union[int, str]
    ) -> bool:
        chat_id = await self.resolve_peer_id(chat_id)
        return await self.auto_execute("post", "leaveChat", locals())
