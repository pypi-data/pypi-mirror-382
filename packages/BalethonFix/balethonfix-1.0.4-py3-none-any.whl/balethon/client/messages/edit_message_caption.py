from typing import Union

import balethon
from ...objects import Message
from balethon import objects


class EditMessageCaption:

    async def edit_message_caption(
            self: "balethon.Client",
            chat_id: Union[int, str],
            message_id: int,
            caption: str,
            reply_markup: "objects.ReplyMarkup" = None
    ) -> Message:
        chat_id = await self.resolve_peer_id(chat_id)
        return await self.auto_execute("post", "editMessageCaption", locals())
