import json
import config
from aiogram import types

from models.gender import GenderModel


class Keyboards:
    def __init__(self):
        pass

    def main_keyboard(self):
        kb = types.ReplyKeyboardMarkup()
        kb.add("⭐️ Оценивать", "📩 Мои оценки")
        kb.add("👤 Профиль", "ℹ️ О нас")
        return kb

    def skip_city_field_keyboard(self):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("Пропустить", callback_data=json.dumps({'action': 'skip_city'})))
        return kb


    def user_menu(self, user_id: int):
        kb = types.InlineKeyboardMarkup(row_width=len(config.TOTAL_MARKS)//2)
        mark_buttons = [types.InlineKeyboardButton(mark, callback_data=json.dumps({'action': 'add_mark', 'm': mark, 'u': user_id}))
                        for mark in config.TOTAL_MARKS]

        kb.add(*mark_buttons)
        kb.add(
            types.InlineKeyboardButton("🛑 Стоп", callback_data=json.dumps({'action': 'main_menu'})),
        )

        return kb

    def profile_menu(self, user_id: int):
        kb = types.InlineKeyboardMarkup()
        kb.add(
            types.InlineKeyboardButton("Изменить имя", callback_data=json.dumps({'action': 'change_profile', 'set': 'name'})),
            types.InlineKeyboardButton("Изменить фото", callback_data=json.dumps({'action': 'change_profile', 'set': 'photo'})),
            types.InlineKeyboardButton("Выбор пола",
                                       callback_data=json.dumps({'action': 'change_profile', 'set': 'gender'})),
            types.InlineKeyboardButton("Изменить город",
                                       callback_data=json.dumps({'action': 'change_profile', 'set': 'city'})),
            types.InlineKeyboardButton("Изменить возраст", callback_data=json.dumps({'action': 'change_profile', 'set': 'age'}))
        )
        return kb

    def back_to(self, action: str, **options):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("↪️ Назад", callback_data=json.dumps({'action': action, **options})))
        return kb

    def choose_city(self, back_to_action: str = 'main_menu'):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📝 Выбрать город", switch_inline_query_current_chat=config.SEARCH_CITY_INLINE_QUERY))
        kb.add(types.InlineKeyboardButton("↪️ Назад", callback_data=json.dumps({'action': back_to_action})))
        return kb

    def choose_gender(self, genders: list[GenderModel], back_to_action: str = 'main_menu'):
        kb = types.InlineKeyboardMarkup()
        btns = [types.InlineKeyboardButton(f"👧🏿 {gender.title}", callback_data=json.dumps({'action': 'registration_gender', 'id': gender.id})) for gender in genders]
        kb.add(*btns)
        kb.add(types.InlineKeyboardButton("↪️ Назад", callback_data=json.dumps({'action': back_to_action})))
        return kb

    def view_marks(self):
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton('▶️ Следующая оценка', callback_data=json.dumps({'action': 'profile_marks'})))
        kb.add(types.InlineKeyboardButton("↪️ Назад", callback_data=json.dumps({'action': 'main_menu'})))
        return kb

