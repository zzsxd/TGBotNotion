import telebot
from telebot import types

class Bot_inline_btns:
    def __init__(self):
        super(Bot_inline_btns, self).__init__()
        self.__markup = types.InlineKeyboardMarkup(row_width=1)

    def start_buttons(self, redirect_url):
        first = types.InlineKeyboardButton('Авторизоваться', url=f"https://api.notion.com/v1/oauth/authorize?client_id=12b0d8ab-cb43-4bbf-b710-70552fd72be5&response_type=code&owner=user&redirect_uri={redirect_url}")
        second = types.InlineKeyboardButton('Готово', callback_data='done')
        t = types.InlineKeyboardButton('Подписка', callback_data='sub')
        self.__markup.add(first, second, t)
        return self.__markup

    def admin_btns(self):
        l = types.InlineKeyboardButton('Выдать лимит', callback_data='givelimit')
        sub = types.InlineKeyboardButton('Выдать подписку', callback_data='givesub')
        newsletter = types.InlineKeyboardButton('Создать рассылку', callback_data='newsletter')
        export = types.InlineKeyboardButton('Экпортировать БД', callback_data='export')
        self.__markup.add(l, sub, newsletter, export)
        return self.__markup

    def newsletter_btns(self):
        done = types.InlineKeyboardButton('Подтвердить', callback_data='newsready')
        cancel = types.InlineKeyboardButton('Отменить', callback_data='newscancel')
        self.__markup.add(done, cancel)
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
        self.__markup.add(f)
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

    def write_note(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        product_catalog = types.KeyboardButton('написать заметку')
        keyboard.add(product_catalog)
        return keyboard

    def choose_statis(self, data):
        out = list()
        print(data)
        for i in data:
            if i in out:
                continue
            else:
                out.append(i)
        markup = types.InlineKeyboardMarkup(row_width=1)
        for index, i in enumerate(out):
            if i[0] not in out:
                z = types.InlineKeyboardButton(i[0], callback_data=f'choose_status{index}')
                markup.add(z)
        return markup

    def notion_db_btns(self, names):
        markup = types.InlineKeyboardMarkup(row_width=1)
        for index, i in enumerate(names):
            z = types.InlineKeyboardButton(i, callback_data=f'notions_dbs{index}')
            markup.add(z)
        return markup