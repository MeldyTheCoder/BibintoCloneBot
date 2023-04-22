import json

import config
from filters import Filters
from database import Database
from keyboards import Keyboards
from debug import Debug
from aiogram import Bot, types, executor, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

app = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot=app, storage=storage)
db = Database(config.DATABASE_PATH)
filters = Filters(db)
kbs = Keyboards()
debugger = Debug()

class Registration(StatesGroup):
    name = State()
    age = State()
    city = State()
    photo = State()



@dp.message_handler(filters.isPrivateMessage(), filters.userNotRegisteredMessage(), content_types=['text'], commands=['start'])
async def start_unregistered(message: types.Message):
    text = f'💬 <b>Добро пожаловать,</b> <code>{message.from_user.first_name}</code>!\n\nВы попали в бот для оценок фото пользователей. Для продолжения нужно пройти регистрацию'
    await message.answer(text)

    await Registration.first()
    await dp.current_state().update_data(user_id=message.chat.id)
    text = '✅ <b>Шаг</b> <code>1/2</code>\n\nКак я могу Вас называть?'
    return await message.answer(text)

@dp.message_handler(filters.isPrivateMessage(), filters.userRegisteredMessage(), content_types=['text'], commands=['start'])
async def start_registered(message: types.Message):
    try:
        text = f'<b>Вы вернулись в главное меню.</b>'
        kb = kbs.main_keyboard()
        await message.answer(text, reply_markup=kb)
    except Exception as e:
        debugger.exception(e)


@dp.message_handler(filters.isPrivateMessage(), filters.userNotRegisteredMessage(), content_types=['text'], state=Registration.name)
async def registration_name(message: types.Message, state: FSMContext):
    try:
        name = message.text
        await state.update_data(name=name)
        text = f'✅ <b>Отлично, шаг</b> <code>{2}/{4}</code>\n<b>Теперь введите Ваш возраст:</b>'
        await Registration.next()
        return await message.answer(text)
    except Exception as e:
        debugger.exception(e)
        text = '🚫 <b>Произошла неизвестная ошибка</b>\n\nПовторите попытку позднее.'
        await state.finish()
        return await message.answer(text)

@dp.message_handler(filters.isPrivateMessage(), filters.userNotRegisteredMessage(), content_types=['text'], state=Registration.age)
async def registration_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        await state.update_data(age=age)
        text = f'✅ <b>Отлично, шаг</b> <code>{3}/{4}</code>\n<b>Теперь введите Ваш город:</b>'
        kb = kbs.skip_city_field_keyboard()
        await Registration.next()
        return await message.answer(text, reply_markup=kb)

    except ValueError:
        text = '🚫 <b>Значение для поля "возраст" должен быть целым числом!</b>'
        return await message.answer(text)

    except Exception as e:
        debugger.exception(e)
        text = '🚫 <b>Произошла неизвестная ошибка</b>\n\nПовторите попытку позднее.'
        await state.finish()
        return await message.answer(text)

@dp.callback_query_handler(filters.query("skip_city"), filters.userNotRegisteredQuery(), filters.isPrivateQuery(), state=Registration.city)
async def skip_city(query: types.CallbackQuery, state: FSMContext):
    try:
        city = None
        await state.update_data(city=city)
        text = f'✅ <b>Отлично, шаг</b> <code>{4}/{4}</code>\n<b>Теперь отправьте Ваше фото:</b>'
        await Registration.next()
        return await app.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text=text, reply_markup=None)

    except Exception as e:
        debugger.exception(e)
        text = '🚫 <b>Произошла неизвестная ошибка</b>\n\nПовторите попытку позднее.'
        await state.finish()
        return await app.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text=text, reply_markup=None)


@dp.message_handler(filters.userNotRegisteredMessage(), filters.isPrivateMessage(), state=Registration.city, content_types=['text'])
async def registration_city(message: types.Message, state: FSMContext):
    try:
        city = message.text
        await state.update_data(city=city)
        text = f'✅ <b>Отлично, шаг</b> <code>{4}/{4}</code>\n<b>Теперь отправьте Ваше фото:</b>'
        await Registration.next()
        return await message.answer(text)

    except Exception as e:
        debugger.exception(e)
        text = '🚫 <b>Произошла неизвестная ошибка</b>\n\nПовторите попытку позднее.'
        await state.finish()
        return await message.answer(text)

@dp.message_handler(filters.userNotRegisteredMessage(), filters.isPrivateMessage(), state=Registration.photo, content_types=['photo'])
async def registration_photo(message: types.Message, state: FSMContext):
    try:
        photo = message.photo[0].file_id
        await state.update_data(city=photo)
        text = f'✅ <b>Вы успешно зарегистрировались!</b>'
        db.add_user(**(await state.get_data()))
        return await message.answer(text)

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
        likes = db.get_likes(from_user=user['id'])
        from_user = likes[-1]['to_user'] if likes else 0
        user_data = db.next_user(from_user)

        if 'u' not in data:
            text = f'👤 <b>{user_data["name"]}, {user_data["city"]}</b>\n\n<b>Возраст</b>: <code>{user_data["age"]} лет</code>'
            photo = user_data['photo']
            kb = kbs.user_menu(user_data['id'])
            return await app.send_photo(query.message.chat.id, photo, caption=text, reply_markup=kb)

        if 'm' not in data:
            pass
            #db.add_like(to_user=)

    except Exception as e:
        debugger.exception(e)
if __name__ == '__main__':
    executor.start_polling(dp, fast=True)