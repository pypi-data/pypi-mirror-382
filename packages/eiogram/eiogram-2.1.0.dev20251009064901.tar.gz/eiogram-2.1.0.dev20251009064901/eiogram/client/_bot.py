from typing import Optional, Union, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..types import (
        User,
        Message,
        InlineKeyboardMarkup,
        BotCommand,
        ChatMemberStatus,
        AnswerInlineQuery,
        Update,
    )


class Bot:
    def __init__(self, token: str):
        self.token = token
        self._get_me = None

    async def is_join(
        self,
        chat_id: Union[str, int],
    ) -> bool:
        from ..types._chat import ChatMemberStatus

        try:
            me = await self.get_me()
            status = await self.get_chat_member(chat_id=chat_id, user_id=me.id)
            if status and status in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.CREATOR,
                ChatMemberStatus.MEMBER,
                ChatMemberStatus.RESTRICTED,
            ]:
                return True
        except Exception:
            return False

    async def is_admin(
        self,
        chat_id: Union[str, int],
    ) -> bool:
        from ..types._chat import ChatMemberStatus

        try:
            me = await self.get_me()
            status = await self.get_chat_member(chat_id=chat_id, user_id=me.id)
            if status and status in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.CREATOR,
            ]:
                return True
        except Exception:
            return False

    async def get_me(self) -> "User":
        from .methods._get_me import GetMe

        if not self._get_me:
            me = await GetMe(self.token).execute()
            self._get_me = me
        return self._get_me

    async def set_webhook(
        self,
        url: str,
        max_connections: int = 40,
        allowed_updates: Optional[List[str]] = [
            "message",
            "callback_query",
            "inline_query",
        ],
        drop_pending_updates: bool = False,
        secret_token: Optional[str] = None,
    ) -> bool:
        from .methods._set_webhook import SetWebhook

        return await SetWebhook(self.token).execute(
            url=url,
            max_connections=max_connections,
            allowed_updates=allowed_updates,
            drop_pending_updates=drop_pending_updates,
            secret_token=secret_token,
        )

    async def restrict_user(
        self,
        chat_id: Union[int, str],
        user_id: int,
        until_date: int,
    ) -> bool:
        from .methods._restrict_user import RestrictUser

        return await RestrictUser(self.token).execute(
            chat_id=chat_id,
            user_id=user_id,
            until_date=until_date,
        )

    async def get_chat_member(
        self,
        chat_id: Union[int, str],
        user_id: int,
    ) -> "ChatMemberStatus":
        from .methods._get_chat_member import GetChatMember

        return await GetChatMember(self.token).execute(
            chat_id=chat_id,
            user_id=user_id,
        )

    async def set_my_commands(
        self,
        commands: list["BotCommand"],
    ) -> bool:
        from .methods._set_my_commands import SetMyCommands

        return await SetMyCommands(self.token).execute(
            commands=commands,
        )

    async def delete_webhook(
        self,
        drop_pending_updates: bool = False,
    ) -> bool:
        from .methods._delete_webhook import DeleteWebhook

        return await DeleteWebhook(self.token).execute(
            drop_pending_updates=drop_pending_updates,
        )

    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
        reply_to_message_id: Optional[int] = None,
    ) -> "Message":
        from .methods._send_message import SendMessage

        return await SendMessage(self.token).execute(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
        )

    async def edit_message(
        self,
        chat_id: Union[int, str],
        message_id: int,
        text: str,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
    ) -> "Message":
        from .methods._edit_message import EditMessage

        return await EditMessage(self.token).execute(
            chat_id=chat_id, message_id=message_id, text=text, reply_markup=reply_markup
        )

    async def edit_message_caption(
        self,
        chat_id: Union[int, str],
        message_id: int,
        caption: Optional[str],
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
    ) -> "Message":
        from .methods._edit_message_caption import EditMessageCaption

        return await EditMessageCaption(self.token).execute(
            chat_id=chat_id,
            message_id=message_id,
            caption=caption,
            reply_markup=reply_markup,
        )

    async def send_photo(
        self,
        chat_id: Union[int, str],
        photo: Union[str, bytes],
        caption: Optional[str] = None,
        reply_markup: Optional["InlineKeyboardMarkup"] = None,
    ) -> "Message":
        from .methods._send_photo import SendPhoto

        return await SendPhoto(self.token).execute(chat_id=chat_id, photo=photo, caption=caption, reply_markup=reply_markup)

    async def pin_message(
        self,
        chat_id: Union[int, str],
        message_id: int,
        disable_notification: bool = False,
    ) -> bool:
        from .methods._pin_message import PinMessage

        return await PinMessage(self.token).execute(
            chat_id=chat_id,
            message_id=message_id,
            disable_notification=disable_notification,
        )

    async def delete_messages(self, chat_id: Union[int, str], message_ids: List[int]) -> List[bool]:
        from .methods._delete_messages import DeleteMessages

        return await DeleteMessages(self.token).execute(chat_id=chat_id, message_ids=message_ids)

    async def answer_callback(
        self,
        callback_query_id: str,
        text: Optional[str] = None,
        show_alert: Optional[bool] = None,
    ) -> bool:
        from .methods._answer_callback import AnswerCallbackQuery

        return await AnswerCallbackQuery(self.token).execute(
            callback_query_id=callback_query_id, text=text, show_alert=show_alert
        )

    async def answer_inline_query(self, answer: "AnswerInlineQuery") -> bool:
        from .methods._answer_inline_query import AnswerInlineQueryMethod

        return await AnswerInlineQueryMethod(self.token).execute(answer=answer)

    async def get_updates(
        self,
        offset: Optional[int] = None,
        limit: int = 100,
        timeout: int = 0,
        allowed_updates: Optional[List[str]] = None,
    ) -> List["Update"]:
        from .methods._get_updates import GetUpdates

        return await GetUpdates(self.token).execute(
            offset=offset,
            limit=limit,
            timeout=timeout,
            allowed_updates=allowed_updates,
        )
