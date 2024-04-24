import base64
import os
import platform
from threading import Lock

import requests
import telebot

from backend import TempUserData, DbAct
from config_parser import ConfigParser
from db import DB
from frontend import Bot_inline_btns

config_name = 'secrets.json'


def main():
    @bot.message_handler(commands=['start'])
    def start_msg(message):
        user_id = message.chat.id
        buttons = Bot_inline_btns()
        command = message.text.replace('/', '')
        if command == 'start':
            db_actions.add_user(user_id, message.from_user.first_name, message.from_user.last_name,
                                f'@{message.from_user.username}')
            bot.send_message(user_id, 'Привет! Я Notes Bot - бот для заметок!\n\n'
                                      'Для начала тебе нужно <b>авторизоваться</b>\n\n'
                                      'Затем выбрать таблицу, которую используешь в качестве <i>Inbox</i>',
                             reply_markup=buttons.start_buttons(), parse_mode='HTML')

    @bot.message_handler(content_types=['text', 'photo'])
    def txt_msg(message):
        user_id = message.chat.id
        bot.send_message(user_id, 'Отлично, ваша заметка сохранена!')

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        user_id = call.message.chat.id
        if db_actions.user_is_existed(user_id):
            if call.data == 'done':
                client_id = "c15749b7-42af-4ad0-a33f-c9bff1b85f68"
                client_secret = "secret_QubBRwsJl8jCit5YapALs08zUXUlBka8cHMWtDXwWMF"
                redirect_uri = "https://t.me/nbnotesbot"

                # Закодируйте учетные данные в формате base64
                encoded = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")

                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {encoded}"
                }
                body = {
                    "grant_type": "authorization_code",
                    "code": "0367dcee-8208-461e-9c46-517ad95eeb71",
                    "redirect_uri": redirect_uri
                }

                # Отправьте запрос на сервер авторизации Notion
                r = requests.post("https://api.notion.com/v1/oauth/token", headers=headers, json=body)
                print('status-code: ', r.status_code)
                if r.status_code == 200:
                    bot.send_message(user_id, '<b>Авторизация успешна!</b>\n\n'
                                              'Теперь ты можешь делать заметки', parse_mode='HTML')
                elif r.status_code == 400 or r.status_code == 401:
                    bot.send_message(user_id, '<b>Авторизация не пройдена!</b>\n\n'
                                              'Попробуйте еще раз!', parse_mode='HTML')
                # bot.send_invoice(user_id, 'Тестовый инвойс', 'тестовый инвойс', 'test_invoice', provider_token=pay, currency='RUB', prices=[types.LabeledPrice('Оплата товара', 100 * 100)])

    bot.polling(none_stop=True)


if '__main__' == __name__:
    os_type = platform.system()
    work_dir = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser(f'{work_dir}/{config_name}', os_type)
    temp_user_data = TempUserData()
    db = DB(config.get_config()['db_file_name'], Lock())
    db_actions = DbAct(db, config, config.get_config()['xlsx_path'])
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    main()
