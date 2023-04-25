import asyncio
import json
import config
import models.exceptions
from filters import Filters
from database import Database
from keyboards import Keyboards
from debug import Debug
from essentials import Essentials
from checkers import CheckerExecutor
from menus import ProfileMenu, UserMarkMenu
from typing import Union
from models.fields import BaseMediaField, BaseTextField
from aiogram import Bot, types, executor, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from states import Registration, ProfileSettings
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State

loop = asyncio.new_event_loop()

app = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML, loop=loop)
storage = MemoryStorage()
dp = Dispatcher(bot=app, storage=storage, loop=loop)
db = Database(config.DATABASE_PATH)
es = Essentials(app)
filters = Filters(db)
kbs = Keyboards()
debugger = Debug()
check = CheckerExecutor(loop=loop, app=app, db=db)
check.run_all()


@dp.message_handler(filters.isPrivateMessage(), filters.userNotRegisteredMessage(), content_types=['text'], commands=['start'])
async def start_unregistered(message: types.Message):
    text = f'💬 <b>Добро пожаловать,</b> <code>{message.from_user.first_name}</code>!\n\nВы попали в бот для оценок фото пользователей. Для продолжения нужно пройти регистрацию'
    await message.answer(text)

    state = await Registration.first()
    await dp.current_state().update_data(user_id=message.chat.id)
    text = Registration.texts[await Registration().get_state_short_name(state=state)][0]
    return await app.send_message(message.chat.id, text)

@dp.callback_query_handler(filters.query('main_menu'), filters.userRegisteredQuery(), filters.isPrivateQuery())
async def main_menu(query: types.CallbackQuery):
    try:
        text = f'<b>Вы вернулись в главное меню.</b>'
        kb = kbs.main_keyboard()
        await es.delete_message(query.message.chat.id, query.message.message_id)
        await es.send_message(query.message.chat.id, text, reply_markup=kb)
    except Exception as e:
        debugger.exception(e)

@dp.message_handler(filters.isPrivateMessage(), filters.userRegisteredMessage(), content_types=['text'], commands=['start'])
async def start_registered(message: types.Message):
    try:
        text = f'<b>Вы вернулись в главное меню.</b>'
        kb = kbs.main_keyboard()
        await message.answer(text, reply_markup=kb)
    except Exception as e:
        debugger.exception(e)

@dp.message_handler(filters.text('⭐️ Оценивать'), filters.isPrivateMessage(), filters.userRegisteredMessage(), content_types=['text'])
async def start_marking(message: types.Message):
    try:
        user = db.get_user(user_id=message.chat.id)

        likes = db.get_likes(from_user=user.id)
        to_user = likes[-1].to_user if likes else 0
        user_data = db.next_user(user.id, to_user)
        if not user_data:
            text = '⛔️ <b>Похоже, что анкеты закончились...</b>\n\nНе переживайте, скоро появятся новые)'
            return await message.answer(text)

        menu = UserMarkMenu(app, dp, user=user)
        photo = user_data.photo
        return await menu.send(message.chat.id, photo)

    except Exception as e:
        debugger.exception(e)
        text = '🚫 <b>Произошла неизвестная ошибка</b>\n\nПовторите попытку позднее.'
        kb = kbs.back_to('main_menu')
        return await es.send_message(message.chat.id, text, reply_markup=kb)


@dp.callback_query_handler(filters.query('profile'), filters.isPrivateQuery(), filters.userRegisteredQuery())
async def view_profile(query: types.CallbackQuery):
    try:
        user = db.get_user(user_id=query.message.chat.id)
        likes = db.get_likes()

        menu = ProfileMenu(app, dp, user=user, likes=likes)
        photo = user.photo
        await menu.edit(query.message.chat.id, query.message.message_id, photo)

    except Exception as e:
        debugger.exception(e)
        text = '🚫 <b>Произошла неизвестная ошибка</b>\n\nПовторите попытку позднее.'
        kb = kbs.back_to('main_menu')
        return await es.edit_message(query.message.chat.id, query.message.message_id, text, reply_markup=kb)

@dp.message_handler(filters.text('👤 Профиль'), filters.isPrivateMessage(), filters.userRegisteredMessage(), content_types=['text'])
async def view_profile(message: types.Message):
    try:
        user = db.get_user(user_id=message.chat.id)
        likes = db.get_likes()

        menu = ProfileMenu(app, dp, user=user, likes=likes)
        photo = user.photo
        await menu.send(message.chat.id, photo)

    except Exception as e:
        debugger.exception(e)
        text = '🚫 <b>Произошла неизвестная ошибка</b>\n\nПовторите попытку позднее.'
        kb = kbs.back_to('main_menu')
        return await es.send_message(message.chat.id, text, reply_markup=kb)
@dp.callback_query_handler(filters.query('profile_marks'), filters.isPrivateQuery(), filters.userRegisteredQuery())
async def profile_marks(query: types.CallbackQuery):
    try:
        likes = db.get_likes_by_time()

    except Exception as e:
        debugger.exception(e)

@dp.message_handler(filters.isPrivateMessage(), filters.userNotRegisteredMessage(), content_types=['text'], state=Registration)
async def registration(message: types.Message, state: FSMContext):
    try:
        state_name = await Registration().get_state_short_name(state)
        field = await Registration().get_field(state_name)

        text_formatted = ''

        if isinstance(field, BaseTextField):
            text = message.text
            text_formatted = field.get_transformed(text)

        elif isinstance(field, BaseMediaField):
            data = getattr(message, field.field_type)
            if isinstance(data, list):
                data = data[0]

            text_formatted = data.file_id

        data = {state_name: text_formatted}
        await state.update_data(**data)

        if await Registration().is_last(state):
            db.add_user(**(await state.get_data()))
            await state.finish()
            text = await Registration().get_text(state_name, index=1)
            kb = await Registration().get_keyboard(state_name)
            return await es.send_message(message.chat.id, text, reply_markup=kb)

        state = await Registration.next()
        state_name = await Registration().get_state_short_name(state)

        text = await Registration().get_text(state_name, index=0)
        kb = await Registration().get_keyboard(state_name)
        return await message.answer(text, reply_markup=kb)

    except models.exceptions.InvalidFieldData:
        text = '🚫 <b>Некорректный ввод данных!</b>\n\nПовторите ввод:'
        kb = kbs.back_to('main_menu')
        return await es.send_message(message.chat.id, text, reply_markup=kb)

    except Exception as e:
        debugger.exception(e)
        await dp.current_state().finish()
        text = '🚫 <b>Произошла неизвестная ошибка</b>\n\nПовторите попытку позднее.'
        return await message.answer(text)

@dp.callback_query_handler(filters.query('change_profile'), filters.isPrivateQuery(), filters.userRegisteredQuery())
async def change_profile_query(query: types.CallbackQuery):
    data = json.loads(query.data)
    try:
        states_names = ProfileSettings().state_short_names
        if 'set' not in data or not data['set']:
            raise models.exceptions.NoOptionsPassed()

        setup = data['set']
        if setup not in states_names:
            raise models.exceptions.NoSuchOption(option=setup)

        text: str = await ProfileSettings().get_text(setup, index=0)
        state: State = getattr(ProfileSettings, setup)

        await state.set()
        kb = await ProfileSettings().get_keyboard(state)
        await es.delete_message(query.message.chat.id, query.message.message_id)
        await es.send_message(query.message.chat.id, text, reply_markup=kb)

    except Exception as e:
        debugger.exception(e)
        await dp.current_state().finish()
        text = '🚫 <b>Произошла неизвестная ошибка</b>\n\nПовторите попытку позднее.'
        kb = kbs.back_to('main_menu')
        return await es.edit_message(query.message.chat.id, query.message.message_id, text, reply_markup=kb)

@dp.message_handler(filters.userRegisteredMessage(), filters.isPrivateMessage(), state=ProfileSettings, content_types=['photo', 'text'])
async def change_profile(message: types.Message, state: FSMContext):
    try:
        user = db.get_user(user_id=message.chat.id)

        state_name = await ProfileSettings().get_state_short_name(state)
        fields = ProfileSettings.fields
        field = fields[state_name]

        text_formatted = ''

        if isinstance(field, BaseTextField):
            text = message.text
            text_formatted = field.get_transformed(text)

        elif isinstance(field, BaseMediaField):
            data = getattr(message, field.field_type)

            if not data:
                raise models.exceptions.InvalidFieldData(type=field.field_type)

            if isinstance(data, list):
                data = data[0]

            text_formatted = data.file_id

        data = {state_name: text_formatted}
        db.update_user(user.id, **data)

        text = await ProfileSettings().get_text(state_name, index=1)
        kb = await ProfileSettings().get_keyboard(state_name)
        await state.finish()
        return await message.answer(text, reply_markup=kb)

    except Exception as e:
        debugger.exception(e)
        text = '🚫 <b>Произошла неизвестная ошибка</b>\n\nПовторите попытку позднее.'
        await state.finish()
        return await message.answer(text)

@dp.callback_query_handler(filters.query("add_mark"), filters.isPrivateQuery(), filters.userRegisteredQuery())
async def add_mark(query: types.CallbackQuery):
    data = json.loads(query.data)
    try:
        user = db.get_user(user_id=query.message.chat.id)

        if 'u' not in data:
            likes = db.get_likes(from_user=user.id)
            to_user = likes[-1].to_user if likes else 0
            user_data = db.next_user(user.id, to_user)
        else:
            user_data = db.next_user(user.id, data['u'])

        if 'm' in data and user_data:
            db.add_like(to_user=user_data.id, from_user=user.id, mark=data['m'])
            user_data = db.next_user(user.id, user_data.id)
            await es.delete_message(query.message.chat.id, query.message.message_id)

        if not user_data:
            text = '🚫 <b>Анкеты закончились(</b>\n\nСкоро появятся.'
            kb = kbs.back_to('main_menu')
            return await es.send_message(text=text, chat_id=query.message.chat.id, reply_markup=kb)

        menu = UserMarkMenu(app, dp, user=user_data)
        photo = user_data.photo
        return await menu.send(query.message.chat.id, photo)

    except Exception as e:
        debugger.exception(e)
        text = '🚫 <b>Произошла неизвестная ошибка</b>\n\nПовторите попытку позднее.'
        kb = kbs.back_to('main_menu')
        return await es.edit_message(text=text, chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=kb)

if __name__ == '__main__':
    executor.start_polling(dp, fast=True)