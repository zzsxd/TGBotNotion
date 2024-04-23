import telebot
from telebot import types

class Bot_inline_btns:
    def __init__(self):
        super(Bot_inline_btns, self).__init__()
        self.__markup = types.InlineKeyboardMarkup(row_width=1)

    def start_buttons(self):
        first = types.InlineKeyboardButton('Авторизоваться', callback_data='property')
        second = types.InlineKeyboardButton('Готово', callback_data='property')
        self.__markup.add(first, second)
        return self.__markup