import telebot
from telebot import types

class Bot_inline_btns:
    def __init__(self):
        super(Bot_inline_btns, self).__init__()
        self.__markup = types.InlineKeyboardMarkup(row_width=1)

    def start_buttons(self):
        first = types.InlineKeyboardButton('Авторизоваться', url="https://api.notion.com/v1/oauth/authorize?client_id=457effbf-b79b-429b-8c3f-b7d7d2ec379d&response_type=code&owner=user&redirect_uri=https%3A%2F%2Fbeba-2a00-1fa0-8236-69b3-14a3-14a6-6781-3ca4.ngrok-free.app")
        second = types.InlineKeyboardButton('Готово', callback_data='done')
        t = types.InlineKeyboardButton('Подписка', callback_data='sub')
        self.__markup.add(first, second, t)
        return self.__markup
    def admin_btns(self):
        l = types.InlineKeyboardButton('Выдать лимит', callback_data='givelimit')
        sub = types.InlineKeyboardButton('Выдать подписку', callback_data='givesub')
        self.__markup.add(l, sub)
        return self.__markup

    def actions_btns(self):
        d1 = types.InlineKeyboardButton('Время истечения подписки', callback_data='restrict0')
        d2 = types.InlineKeyboardButton('Количество заметок', callback_data='restrict1')
        self.__markup.add(d1, d2)
        return self.__markup

    def payment_btn(self):
        f = types.InlineKeyboardButton('1 месяц - 299₽', callback_data='subscription0')
        s = types.InlineKeyboardButton('6 месяцев - 1399₽', callback_data='subscription1')
        t = types.InlineKeyboardButton('12 месяцев - 2599₽', callback_data='subscription2')
        z = types.InlineKeyboardButton('30 запросов на месяц - 99₽', callback_data='subscription3')
        self.__markup.add(f, s, t, z)
        return self.__markup

    def cnt_btn(self):
        f = types.InlineKeyboardButton('1 месяц', callback_data='cnt0')
        s = types.InlineKeyboardButton('6 месяцев', callback_data='cnt1')
        t = types.InlineKeyboardButton('12 месяцев', callback_data='cnt2')
        z = types.InlineKeyboardButton('30 запросов на месяц', callback_data='cnt3')
        self.__markup.add(f, s, t, z)
        return self.__markup

    def choose_notion_dest(self):
        f = types.InlineKeyboardButton('базу данных', callback_data='select_dst0')
        s = types.InlineKeyboardButton('поле', callback_data='select_dst1')
        rr = types.InlineKeyboardButton('режим работы', callback_data='select_dst12')
        self.__markup.add(f, s, rr)
        return self.__markup

    def mods_btns(self):
        f = types.InlineKeyboardButton('обычный', callback_data='change_mod0')
        s = types.InlineKeyboardButton('расширенный', callback_data='change_mod1')
        self.__markup.add(f, s)
        return self.__markup

    def additions_btns(self):
        f = types.InlineKeyboardButton('дату', callback_data='add_addition0')
        s = types.InlineKeyboardButton('статус', callback_data='add_addition1')
        self.__markup.add(f, s)
        return self.__markup

    def notion_db_btns(self, names):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for index, i in enumerate(names):
            z = types.InlineKeyboardButton(i, callback_data=f'notions_dbs{index}')
            markup.add(z)
        return markup

    def notion_prop_btns(self, names):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for index, i in enumerate(names):
            z = types.InlineKeyboardButton(i, callback_data=f'notions_props{index}')
            markup.add(z)
        return markup