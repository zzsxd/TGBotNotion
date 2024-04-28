import base64
import os
import platform
import time
import types
from threading import Lock
import json
import requests
import telebot
from telebot import types
from datetime import datetime
from backend import TempUserData, DbAct
from config_parser import ConfigParser
from db import DB
from frontend import Bot_inline_btns

config_name = 'secrets.json'


def give_sub(user_id, nick_name, sub_type):
    match sub_type:
        case 0:
            db_actions.give_subscription(nick_name, time.time() + 2629746, 0)
        case 1:
            db_actions.give_subscription(nick_name, time.time() + 15778476, 1)
        case 2:
            db_actions.give_subscription(nick_name, time.time() + 31556952, 2)
        case 3:
            db_actions.give_subscription(nick_name, time.time() + 2629746, 3, 30)
    bot.send_message(user_id, 'Операция успешно завершена')


def add_sub(user_id, sub_type):
    match sub_type:
        case '0':
            db_actions.give_subscription(user_id, time.time() + 2629746, 0)
        case '1':
            db_actions.give_subscription(user_id, time.time() + 15778476, 1)
        case '2':
            db_actions.give_subscription(user_id, time.time() + 31556952, 2)
        case '3':
            db_actions.give_subscription(user_id, time.time() + 2629746, 3, 30)


def get_name_db(user_id):
    names = list()
    data = db_actions.get_notion_db(user_id)
    for i in data:
        names.append(i[1])
    return names[temp_user_data.temp_data(user_id)[user_id][3]]


def choose_notion_db(user_id):
    buttons = Bot_inline_btns()
    names = list()
    data = db_actions.get_notion_db(user_id)
    for i in data:
        names.append(i[1])
    bot.send_message(user_id, 'Выберите базу данных из Notion', reply_markup=buttons.notion_db_btns(names))


def get_notion_links(user_id, data):
    out = list()
    print(data)
    for i in data['results']:
        if i["object"] == "database":
            out.append([i['id'], i['title'][0]['plain_text'], i['url']])
    db_actions.update_notion_db(user_id, out)
    choose_notion_db(user_id)


def main():
    @bot.message_handler(commands=['start', 'admin'])
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
        elif command[:5] == 'start':
            temp_user_data.temp_data(user_id)[user_id][2] = command[11:]
        elif db_actions.user_is_admin(user_id):
            if command == 'admin':
                bot.send_message(user_id, 'Вы успешно зашли в админ-панель!', reply_markup=buttons.admin_btns())

    @bot.message_handler(content_types=['text', 'photo'])
    def txt_msg(message):
        user_id = message.chat.id
        user_input = message.text
        button = Bot_inline_btns()
        code = temp_user_data.temp_data(user_id)[user_id][0]
        if db_actions.user_is_existed(user_id):
            if db_actions.check_subscription(user_id):
                match code:
                    case 0:  # выдать лимит
                        if user_input is not None:
                            temp_user_data.temp_data(user_id)[user_id][1] = user_input
                            temp_user_data.temp_data(user_id)[user_id][0] = 3
                            bot.send_message(user_id, 'Что Вы хотите изменить?', reply_markup=button.actions_btns())
                        else:
                            bot.send_message(user_id, 'это не текст, попробуйте ещё раз')
                    case 1:  # выдать подписку
                        if user_input is not None:
                            temp_user_data.temp_data(user_id)[user_id][1] = user_input
                            temp_user_data.temp_data(user_id)[user_id][0] = 2
                            bot.send_message(user_id, 'Выберите тип подписки', reply_markup=button.cnt_btn())
                        else:
                            bot.send_message(user_id, 'это не текст, попробуйте ещё раз')
                    case 4:
                        try:
                            db_actions.update_subscription_time(temp_user_data.temp_data(user_id)[user_id][1],
                                                                datetime.strptime(user_input, '%d-%m-%Y %H:%M').timestamp())
                            temp_user_data.temp_data(user_id)[user_id][0] = None
                            bot.send_message(user_id, 'Операция успешно завершена')
                        except:
                            bot.send_message(user_id, 'неправильный формат даты, попробуйте ещё раз')
                    case 5:
                        try:
                            db_actions.update_subscription_notes(temp_user_data.temp_data(user_id)[user_id][1],
                                                                 int(user_input))
                            temp_user_data.temp_data(user_id)[user_id][0] = None
                            bot.send_message(user_id, 'Операция успешно завершена')
                        except:
                            bot.send_message(user_id, 'это не число, попробуйте ещё раз')
                    case 6:
                        if user_input is not None:
                            headers = {
                                'Authorization': 'Bearer ' + db_actions.get_notion_access_token(user_id),
                                'Content-Type': 'application/json',
                                'Notion-Version': '2022-06-28'
                            }

                            data = {
                                "parent": {"database_id": db_actions.get_db_notion_id(user_id, get_name_db(user_id))},
                                "properties": {
                                    "Responsible": {
                                        "title": [
                                            {
                                                "text": {
                                                    "content": "Tuscan Kale"
                                                }
                                            }
                                        ]
                                    },
                                    "Description": {
                                        "rich_text": [
                                            {
                                                "text": {
                                                    "content": user_input
                                                }
                                            }
                                        ]
                                    },
                                },
                            }
                            response = requests.post('https://api.notion.com/v1/pages', headers=headers,
                                                     json=data)
                            print(response.json())
                            print('done')

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        user_id = call.message.chat.id
        button = Bot_inline_btns()
        if db_actions.user_is_existed(user_id):
            code = temp_user_data.temp_data(user_id)[user_id][0]
            if not db_actions.check_subscription(user_id):
                if db_actions.user_is_admin(user_id):
                    if call.data == 'givelimit':
                        temp_user_data.temp_data(user_id)[user_id][0] = 0
                        bot.send_message(user_id,
                                         'Введите <i><b>никнейм пользователя</b></i>, которому нужно выдать лимит',
                                         parse_mode='HTML')
                    elif call.data == 'givesub':
                        temp_user_data.temp_data(user_id)[user_id][0] = 1
                        bot.send_message(user_id,
                                         'Введите <i><b>никнейм пользователя</b></i>, которому нужно выдать подписку',
                                         parse_mode='HTML')
                    elif call.data[:8] == 'restrict' and code == 3:
                        match call.data[8:]:
                            case '0':
                                temp_user_data.temp_data(user_id)[user_id][0] = 4
                                bot.send_message(user_id,
                                                 'Введите новую дату истечения подписки в формате (31-07-1999 15:50)')
                            case '1':
                                temp_user_data.temp_data(user_id)[user_id][0] = 5
                                bot.send_message(user_id, 'Введите новое количество доступных заметок')
                    elif call.data[:3] == 'cnt' and code == 2:
                        give_sub(user_id, temp_user_data.temp_data(user_id)[user_id][1], int(call.data[3:]))
                if call.data == 'sub':
                    subsc = db_actions.get_eol(user_id)
                    if subsc[2] == 3:
                        bot.send_message(user_id, 'Выберите подписку!\n\n'
                                                  f'Ваша подписка доступна до: {datetime.utcfromtimestamp(subsc[0]).strftime("%Y-%m-%d %H:%M")}\n Заметок осталось: {subsc[1]}',
                                         reply_markup=button.payment_btn())
                    else:
                        bot.send_message(user_id, 'Выберите подписку!\n\n'
                                                  f'Ваша подписка доступна до: {datetime.utcfromtimestamp(subsc[0]).strftime("%Y-%m-%d %H:%M")}',
                                         reply_markup=button.payment_btn())
                elif call.data[:12] == 'subscription':
                    match call.data[12:]:
                        case '0':
                            bot.send_invoice(user_id, '1 месяц - 299₽', 'покупка у Notion Bot', '0',
                                             provider_token=config.get_config()['payment_api'],
                                             currency='RUB', prices=[types.LabeledPrice('Оплата товара', 299 * 100)])
                        case '1':
                            bot.send_invoice(user_id, '6 месяцев - 1399₽', 'покупка у Notion Bot', '1',
                                             provider_token=config.get_config()['payment_api'],
                                             currency='RUB', prices=[types.LabeledPrice('Оплата товара', 1399 * 100)])
                        case '2':
                            bot.send_invoice(user_id, '1 год - 2599₽', 'покупка у Notion Bot', '2',
                                             provider_token=config.get_config()['payment_api'],
                                             currency='RUB',
                                             prices=[types.LabeledPrice('Оплата товара', 2599 * 100)])
                        case '3':
                            bot.send_invoice(user_id, '30 запросов на 30 дней - 99₽', 'покупка у Notion Bot', '3',
                                             provider_token=config.get_config()['payment_api'], currency='RUB',
                                             prices=[types.LabeledPrice('Оплата товара', 99 * 100)])
            else:
                if call.data == 'done':
                    encoded = base64.b64encode(
                        f"{config.get_config()['notion_client_id']}:{config.get_config()['notion_client_secret']}".encode(
                            "utf-8")).decode("utf-8")
                    headers = {
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "Authorization": f"Basic {encoded}"
                    }
                    body = {
                        "grant_type": "authorization_code",
                        "code": temp_user_data.temp_data(user_id)[user_id][2],
                        "redirect_uri": config.get_config()['notion_redirect_uri']
                    }
                    # Отправьте запрос на сервер авторизации Notion
                    r = requests.post("https://api.notion.com/v1/oauth/token", headers=headers, json=body)
                    print(r.json())
                    if r.status_code == 200:
                        notion_token = r.json()['access_token']
                        db_actions.update_notion_token(notion_token, user_id)
                        url = "https://api.notion.com/v1/search"
                        payload = {"page_size": 100}
                        headers = {
                            "accept": "application/json",
                            "Notion-Version": "2022-06-28",
                            "content-type": "application/json",
                            "authorization": f"Bearer {notion_token}"
                        }
                        response = requests.post(url, json=payload, headers=headers)
                        get_notion_links(user_id, response.json())  # тут есть данные про страницы которые чел выбрал, нужно их взять и вывести в кнопки для frontend, чтобы можно было переключаться
                    else:
                        bot.send_message(user_id, '<b>Авторизация не пройдена!</b>\n\n'
                                                  'Попробуйте еще раз!', parse_mode='HTML')
                elif call.data[:11] == 'notions_dbs':
                    temp_user_data.temp_data(user_id)[user_id][0] = 6
                    temp_user_data.temp_data(user_id)[user_id][3] = int(call.data[11:])
                    bot.send_message(user_id, 'Отлично, теперь вы можете оставлять заметки!')


        else:
            bot.send_message(user_id, '<b>Ошибка!</b>\n\n'
                                      'Введите /start', parse_mode='HTML')

    @bot.shipping_query_handler(func=lambda query: True)
    def shipping(shipping_query):
        bot.answer_shipping_query(shipping_query.id, ok=True, shipping_options=[])

    @bot.pre_checkout_query_handler(func=lambda query: True)
    def checkout(pre_checkout_query):
        bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

    @bot.message_handler(content_types=['successful_payment'])
    def got_payment(message):
        user_id = message.from_user.id
        data = message.successful_payment.invoice_payload
        add_sub(user_id, data)
        bot.send_message(user_id, "Спасибо за покупку!")

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
