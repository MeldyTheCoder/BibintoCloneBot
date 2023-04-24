from aiogram import types, Bot, Dispatcher
from typing import Union

import config


class Essentials:
    file_types = ['document', 'voice', 'video', 'photo', 'audio', 'text']

    def __init__(self, app: Bot):
        self.app = app
        self.actions = {'photo': self.app.send_photo, 'document': self.app.send_document, 'video': self.app.send_video,
                   'audio': self.app.send_audio, 'voice': self.app.send_voice}

    async def send_message(self, chat_id: int, text: str, reply_markup: Union[types.InlineKeyboardMarkup, types.ReplyKeyboardMarkup] = '', **options):
        return await self.app.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, **options)

    async def edit_message(self, chat_id: int, message_id: int, text: str, reply_markup: types.InlineKeyboardMarkup = '', **options):
        try:
            return await self.app.edit_message_text(text=text, chat_id=chat_id, message_id=message_id, reply_markup=reply_markup, **options)
        except:
            return await self.app.edit_message_caption(caption=text, chat_id=chat_id, message_id=message_id, reply_markup=reply_markup, **options)

    async def delete_message(self, chat_id: int, message_id: int):
        try:
            return await self.app.delete_message(chat_id, message_id)
        except:
            pass

    async def remove_markup(self, chat_id: int, message_id: int):
        return await self.app.edit_message_reply_markup(chat_id, message_id, reply_markup='')

    async def finish_state(self, dp: Dispatcher, **options):
        try:
            state = dp.current_state(**options)
            await state.finish()
        except:
            pass

    async def send_file(self, chat_id: int, file_id: str, file_type: str, caption: str = "", reply_markup: types.InlineKeyboardMarkup = ''):
        if not file_type in self.file_types:
            return
        try:
            args = {'chat_id': chat_id, file_type: file_id, 'reply_markup': reply_markup, 'caption': caption}
            return await self.actions[file_type](**args)
        except:
            pass

    async def user_href(self, id: int):
        try:
            chat = await self.get_chat(id)
            if not chat:
                raise
            name = chat.first_name
        except:
            name = 'заблокированный пользователь'
        return f'<a href="tg://user?id={id}">{name}</a>'

    async def get_chat(self, chat_id: int):
        try:
            return await self.app.get_chat(chat_id)
        except:
            return
