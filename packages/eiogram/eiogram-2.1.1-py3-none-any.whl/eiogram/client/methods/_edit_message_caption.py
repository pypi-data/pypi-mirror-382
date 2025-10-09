from typing import Optional, Union
from eiogram.types import Message, InlineKeyboardMarkup
from ._base import MethodBase


class EditMessageCaption(MethodBase):
    async def execute(
        self,
        caption: str,
        chat_id: Optional[Union[int, str]] = None,
        message_id: Optional[int] = None,
        inline_message_id: Optional[str] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        data = {
            "caption": caption,
            "parse_mode": "HTML",
        }

        if reply_markup:
            data["reply_markup"] = reply_markup.dict()

        if inline_message_id:
            data["inline_message_id"] = inline_message_id
        else:
            data.update({"chat_id": chat_id, "message_id": message_id})

        response = await self._make_request("POST", "editMessageCaption", data)
        return Message(**response["result"])
