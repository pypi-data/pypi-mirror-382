from typing import Union, BinaryIO

import balethon
from ...objects import InputMedia, resolve_media, Message, ReplyMarkup


class SendAudio:

    async def send_audio(
            self: "balethon.Client",
            chat_id: Union[int, str],
            audio: Union[str, bytes, BinaryIO, InputMedia],
            caption: str = None,
            duration: int = None,
            title: str = None,
            reply_markup: ReplyMarkup = None,
            reply_to_message_id: int = None
    ) -> Message:
        chat_id = await self.resolve_peer_id(chat_id)
        audio = resolve_media(audio)
        return await self.auto_execute("post", "sendAudio", locals())
