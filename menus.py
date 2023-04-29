import config
from aiogram import types, Bot, Dispatcher
from typing import Union
from essentials import Essentials
from debug import Debug
from keyboards import Keyboards
from abc import abstractmethod
from models.like import LikeModel
from models.user import UserModel
from types import FunctionType, LambdaType

debugger = Debug()
kbs = Keyboards()

class BaseMenu:
    text: str = 'Sample Text'
    reply_markup: Union[FunctionType, LambdaType] = None


    def __init__(self, app: Bot, dp: Dispatcher, **options):
        self.__app: Bot = app
        self.__es: Essentials = Essentials(self.__app)
        self.__dp: Dispatcher = dp
        self.keyboard = None
        self.options = options
        self.format_menu()

    @abstractmethod
    def format_menu(self):
        pass

    def get_keyboard(self, **options):
        return self.reply_markup(**options)

    async def send(self, chat_id: int, photo: str = None):
        try:
            if not photo:
                return await self.__es.send_message(chat_id, self.text, reply_markup=self.keyboard)
            return await self.__app.send_photo(chat_id, photo=photo, caption=self.text, reply_markup=self.keyboard)

        except Exception as e:
            debugger.exception(e)

    async def reply(self, chat_id: int, message_id: int):
        pass

    async def edit(self, chat_id: int, message_id: int, photo: str = None):
        try:
            if photo:
                await self.__app.delete_message(chat_id, message_id)
                return await self.send(chat_id, photo)

            return await self.__es.edit_message(chat_id, message_id, self.text, reply_markup=self.keyboard)
        except Exception as e:
            debugger.exception(e)



class ProfileMenu(BaseMenu):
    text = '''
👤 <b>{user_name}, {city}</b>

🤩 <b>Ваша средняя оценка</b>: <code>{likes_avg}/{max_mark}</code>

🔞 <b>Возраст</b>: <code>{age} лет</code>
☦️ <b>Пол</b>: <code>{gender}</code>

🌟 <b>Оценено</b>: <code>{likes_outgoing} чел.</code>
⭐️ <b>Вас оценили</b>: <code>{likes_incoming} чел.</code>
    '''

    reply_markup = staticmethod(lambda user_id: kbs.profile_menu(user_id))

    def format_menu(self):
        user: UserModel = self.options['user']
        likes: list[LikeModel] = self.options['likes']
        likes_incoming: list[LikeModel] = list(filter(lambda like: like and like.to_user.id == user.id, likes))
        likes_outgoing: list[LikeModel] = list(filter(lambda like: like and like.from_user.id == user.id, likes))

        data = {
            'user_name': user.name.first_name,
            'city': user.city.city if user.city.city else 'город не указан',
            'likes_avg': sum([like.mark for like in likes_incoming]) / len(likes_incoming) if likes_incoming else 0,
            'max_mark': max(config.TOTAL_MARKS),
            'gender': user.gender.title,
            'likes_outgoing': len(likes_outgoing),
            'likes_incoming': len(likes_incoming),
            'age': user.age.years
        }

        self.text = self.text.format(**data)
        self.keyboard = self.get_keyboard(user_id=user.id)


class UserMarkMenu(BaseMenu):
    text = '''
👤 <b>{user_name}, {city}</b>
    
🔞 <b>Возраст</b>: <code>{age} лет</code>
☦️ <b>Пол</b>: <code>{gender}</code>
'''

    reply_markup = staticmethod(lambda user_id: kbs.user_menu(user_id))


    def format_menu(self):
        user: UserModel = self.options['user']

        data = {
            'user_name': user.name.first_name,
            'city': user.city.city if user.city.city else 'город не указан',
            'age': user.age.years,
            'gender': user.gender.title
        }

        self.text = self.text.format(**data)
        self.keyboard = self.get_keyboard(user_id=user.id)

class ProfileMarkMenu(BaseMenu):
    text = """
👤 <b>{user_name}, {city}</b>

🔞 <b>Возраст</b>: <code>{age} лет</code>

⭐️ <b>Оценка</b>: <code>{mark}</code>
"""
    reply_markup = staticmethod(lambda: kbs.view_marks())

    def format_menu(self):
        like: LikeModel = self.options['like']

        city = like.from_user.city.city

        data = {
            "user_name": like.from_user.name.first_name,
            "city": city if city else 'город не указан',
            "age": like.from_user.age.years,
            "mark": like.mark
        }

        self.text = self.text.format(**data)
        self.keyboard = self.get_keyboard()

