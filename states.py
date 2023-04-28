from keyboards import Keyboards
from models.fields import BaseTextField, BaseMediaField, PhotoField, IntegerField, StringField, CallbackQueryField
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from typing import Union
from types import FunctionType, LambdaType

kbs = Keyboards()

class CustomStatesGroup(StatesGroup):
    fields: dict[str, Union[BaseMediaField, BaseTextField]] = {}
    keyboards: dict[str, FunctionType] = {}
    texts: dict[str, tuple[str]] = {}

    @property
    def state_short_names(self) -> list[str]:
        return [state.replace(f'{self._group_name}:', '') for state in self._state_names]

    async def get_state_short_name(self, state: Union[str, State, FSMContext]) -> str:
        if isinstance(state, State):
            state = state.state

        elif isinstance(state, FSMContext):
            state = str(await state.get_state())

        return state.replace(f'{self._group_name}:', '')

    async def is_last(self, state: Union[str, State, FSMContext]):
        state = await self.get_state_short_name(state)
        return self.state_short_names[-1] == state


    async def get_keyboard(self, state: Union[str, State, FSMContext], **options):
        state_name = await self.get_state_short_name(state)
        if state_name not in self.keyboards:
            return None

        kb = self.keyboards[state_name]
        if isinstance(kb, FunctionType) or isinstance(kb, LambdaType):
            kb = kb(**options)

        return kb


    async def get_text(self, state: Union[str, State, FSMContext], index: int = 0):
        state_name = await self.get_state_short_name(state)
        if state_name not in self.texts:
            return "<b>*без комментариев*</b>"

        texts = self.texts[state_name]
        if not texts:
            return "<b>*без комментариев*</b>"

        return texts[index] if index in range(len(texts)) else "<b>*без комментариев*</b>"

    async def get_field(self, state: Union[str, State, FSMContext]):
        state_name = await self.get_state_short_name(state)
        if state_name not in self.fields:
            return StringField()
        return self.fields[state_name]


class Registration(CustomStatesGroup):
    name = State()
    age = State()
    city = State()
    gender = State()
    photo = State()

    texts = {"name": (f"💬 <b>Шаг</b> <code>1/5</code>\n\nВведите Ваше имя:",
                      "✅ <b>Вы успешно зарегистрировались</b>"),

             "age": ("💬 <b>Шаг</b> <code>2/5</code>\n\nВведите Ваш возраст:",
                      "✅ <b>Вы успешно зарегистрировались</b>"),

             "city": ("💬 <b>Шаг</b> <code>3/5</code>\n\nВведите название Вашего города:",
                      "✅ <b>Вы успешно зарегистрировались</b>"),

             "gender": ("💬 <b>Шаг</b> <code>4/5</code>\n\nВыберите Ваш пол:",
                      "✅ <b>Вы успешно зарегистрировались</b>"),

             "photo": ("💬 <b>Шаг</b> <code>5/5</code>\n\nОтправьте Ваше фото:",
                      "✅ <b>Вы успешно зарегистрировались</b>")
             }

    fields = {
        "name": StringField(),
        "age": IntegerField(),
        "city": StringField(),
        "gender": CallbackQueryField(returns_key='id', id=int),
        "photo": PhotoField()
    }

    keyboards = {
        "name": kbs.back_to('main_menu'),
        "age": kbs.back_to('main_menu'),
        "city": kbs.choose_city(back_to_action='main_menu'),
        "gender": lambda **kwargs: kbs.choose_gender(kwargs['db'].get_genders(), back_to_action='main_menu'),
        "photo": kbs.back_to('main_menu')
    }


class ProfileSettings(CustomStatesGroup):
    name = State()
    age = State()
    city = State()
    gender = State()
    photo = State()

    texts = {'name': ('📝 <b>Введите Ваше новое отображаемое имя:</b>',
                      '✅ <b>Ваше имя успешно изменено!</b>'),

             'age': ('📝 <b>Укажите Ваш возраст:</b>',
                     '✅ <b>Ваш возраст успешно изменен!</b>'),

             'city': ('📝 <b>Введите название Вашего города:</b>',
                      '✅ <b>Ваш город успешно изменен!</b>'),

             'gender': ('📝 <b>Выберите Ваш пол:</b>',
                        '✅ <b>Ваш пол успешно изменен!</b>'),

             'photo': ('📝 <b>Отправьте Ваше новое отображаемое фото:</b>',
                       '✅ <b>Ваше фото успешно изменено!</b>')
             }

    fields = {
        "name": StringField(),
        "age": IntegerField(),
        "city": StringField(),
        "gender": CallbackQueryField(returns_key='id', id=int),
        "photo": PhotoField()
    }

    keyboards = {
        "name": kbs.back_to('profile'),
        "age": kbs.back_to('profile'),
        "city": kbs.choose_city(back_to_action='profile'),
        "gender": lambda **kwargs: kbs.choose_gender(kwargs['db'].get_genders(), back_to_action='profile'),
        "photo": kbs.back_to('profile')
    }

