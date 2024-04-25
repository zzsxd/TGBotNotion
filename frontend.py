import telebot
from telebot import types

class Bot_inline_btns:
    def __init__(self):
        super(Bot_inline_btns, self).__init__()
        self.__markup = types.InlineKeyboardMarkup(row_width=1)

    def start_buttons(self):
        first = types.InlineKeyboardButton('Авторизоваться', url="https://api.notion.com/v1/oauth/authorize?client_id=c15749b7-42af-4ad0-a33f-c9bff1b85f68&response_type=code&owner=user&redirect_uri=https%3A%2F%2Ft.me%2Fnbnotesbot")
        second = types.InlineKeyboardButton('Готово', callback_data='done')
        t = types.InlineKeyboardButton('Подписка', callback_data='sub')
        self.__markup.add(first, second, t)
        return self.__markup
    def admin_btns(self):
        l = types.InlineKeyboardButton('Выдать лимит', callback_data='givelimit')
        sub = types.InlineKeyboardButton('Выдать подписку', callback_data='givesub')
        self.__markup.add(l, sub)
        return self.__markup

    def payment_btn(self):
        f = types.InlineKeyboardButton('1 месяц - 299₽', callback_data='month')
        s = types.InlineKeyboardButton('6 месяцев - 1399₽', callback_data='sixmonths')
        t = types.InlineKeyboardButton('12 месяцев - 2599₽', callback_data='oneyear')
        z = types.InlineKeyboardButton('30 запросов на месяц - 99₽', callback_data='zapros')
        self.__markup.add(f, s, t, z)
        return self.__markup