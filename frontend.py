from telebot import types

class Bot_inline_btns:
    def __init__(self):
        super(Bot_inline_btns, self).__init__()
        self.__markup = types.InlineKeyboardMarkup(row_width=1)

    def start_buttons(self):
        first = types.InlineKeyboardButton('Авторизоваться', url="https://api.notion.com/v1/oauth/authorize?client_id=c15749b7-42af-4ad0-a33f-c9bff1b85f68&response_type=code&owner=user&redirect_uri=https%3A%2F%2Ft.me%2Fnbnotesbot")
        second = types.InlineKeyboardButton('Готово', callback_data='done')
        self.__markup.add(first, second)
        return self.__markup