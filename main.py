import base64
import os
import platform
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
        elif db_actions.user_is_admin(user_id):
            if command == 'admin':
                bot.send_message(user_id, 'Вы успешно зашли в админ-панель!', reply_markup=buttons.admin_btns())

    @bot.message_handler(content_types=['text', 'photo'])
    def txt_msg(message):
        user_id = message.chat.id
        user_input = message.text
        code = temp_user_data.temp_data(user_id)[user_id][0]
        if db_actions.user_is_existed(user_id):
            match code:
                case 0:  # выдать лимит
                    if user_input is not None:
                        bot.send_message(user_id, 'Лимит успешно выдан')
                case 1:  # выдать подписку
                    if user_input is not None:
                        bot.send_message(user_id, 'Подписка успешна выдана')

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        user_id = call.message.chat.id
        button = Bot_inline_btns()
        # exp_date = db_actions.get_exp_date(user_id) # узнать до какого времени подписка
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
                    "code": "0311105c-4a8d-45ba-b1bf-e47c210b1666",
                    "redirect_uri": redirect_uri
                }

                # Отправьте запрос на сервер авторизации Notion
                r = requests.post("https://api.notion.com/v1/oauth/token", headers=headers, json=body)
                print('status-code: ', r.status_code)
                print(r.json())
                notion_token = r.json()['access_token']
                print(notion_token)
                if r.status_code == 200:
                    bot.send_message(user_id, '<b>Авторизация успешна!</b>\n\n'
                                              'Теперь ты можешь делать заметки', parse_mode='HTML')
                    url = "https://api.notion.com/v1/search"

                    payload = {"page_size": 100}
                    headers = {
                        "accept": "application/json",
                        "Notion-Version": "2022-06-28",
                        "content-type": "application/json",
                        "authorization": f"Bearer {notion_token}"
                    }

                    response = requests.post(url, json=payload, headers=headers)
                    print(
                        response.json())  # тут есть данные про страницы которые чел выбрал, нужно их взять и вывести в кнопки для frontend, чтобы можно было переключаться

                    database_data = response.json()['results']
                    notion_database_id = database_data[0]['id']

                    example_data = {
                        "handle": "@SomeHandle",
                        "tweet": "Here is a tweet"
                    }
                    headers = {
                        'Authorization': 'Bearer ' + notion_token,
                        'Content-Type': 'application/json',
                        'Notion-Version': '2021-08-16'
                    }

                    payload = {
                        'parent': {'database_id': notion_database_id},
                        'properties': {
                            'title': {
                                'title': [
                                    {
                                        'text': {
                                            'content': example_data['handle']
                                        }
                                    }
                                ]
                            },
                            'tweet': {
                                'rich_text': [
                                    {
                                        'type': 'text',
                                        'text': {
                                            'content': example_data['tweet']
                                        }
                                    }
                                ]
                            }
                        }
                    }

                    response = requests.post('https://api.notion.com/v1/pages', headers=headers,
                                             data=json.dumps(payload))

                elif r.status_code != 200:
                    bot.send_message(user_id, '<b>Авторизация не пройдена!</b>\n\n'
                                              'Попробуйте еще раз!', parse_mode='HTML')
            elif call.data == 'sub':
                bot.send_message(user_id, 'Выберите подписку!\n\n'
                                          f'Ваша подписка доступна до: сюда 144 лайн', reply_markup=button.payment_btn())
                # {datetime.utcfromtimestamp(exp_date).strftime("%Y-%m-%d %H:%M")} # в 143 лайн
            elif call.data == 'month':
                bot.send_invoice(user_id, '1 месяц - 299₽', 'покупка у Notion Bot', 'invoice', provider_token=pay,
                                 currency='RUB', prices=[types.LabeledPrice('Оплата товара', 299 * 100)])
            elif call.data == 'sixmonth':
                bot.send_invoice(user_id, '6 месяцев - 1399₽', 'покупка у Notion Bot', 'invoice', provider_token=pay,
                                 currency='RUB', prices=[types.LabeledPrice('Оплата товара', 1399 * 100)])
            elif call.data == 'oneyear':
                bot.send_invoice(user_id, '1 год - 2599₽', 'покупка у Notion Bot', 'invoice', provider_token=pay,
                                 currency='RUB', prices=[types.LabeledPrice('Оплата товара', 2599 * 100)])
            elif call.data == 'zapros':
                bot.send_invoice(user_id, '30 запросов на 30 дней - 1399₽', 'покупка у Notion Bot', 'invoice',
                                 provider_token=pay, currency='RUB',
                                 prices=[types.LabeledPrice('Оплата товара', 1399 * 100)])
            elif call.data == 'givelimit':
                bot.send_message(user_id, 'Введите <i><b>никнейм пользователя</b></i>, которому нужно выдать лимит',
                                 parse_mode='HTML')
                temp_user_data.temp_data(user_id)[user_id][0] = 0
            elif call.data == 'givesub':
                bot.send_message(user_id, 'Введите <i><b>никнейм пользователя</b></i>, которому нужно выдать подписку',
                                 parse_mode='HTML')
                temp_user_data.temp_data(user_id)[user_id][0] = 1
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
        bot.send_message(message.chat.id, "Спасибо за покупку!")

    bot.polling(none_stop=True)


if '__main__' == __name__:
    os_type = platform.system()
    work_dir = os.path.dirname(os.path.realpath(__file__))
    config = ConfigParser(f'{work_dir}/{config_name}', os_type)
    temp_user_data = TempUserData()
    db = DB(config.get_config()['db_file_name'], Lock())
    db_actions = DbAct(db, config, config.get_config()['xlsx_path'])
    pay = config.get_config()['payment_api']
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    main()
