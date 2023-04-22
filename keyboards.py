import json
import config
from aiogram import types

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
        return kb


