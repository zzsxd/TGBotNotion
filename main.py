import base64
import copy
import os
import threading
from pyngrok import ngrok
import pyshorteners
import platform
import time
import types
from threading import Lock
import requests
import telebot
from telebot import types
from datetime import datetime
from backend import TempUserData, DbAct
from config_parser import ConfigParser, RequestsParser
from flask import Flask, request, redirect
from db import DB
from frontend import Bot_inline_btns

config_name = 'secrets.json'
json_paths = ['queries/base_query.json', 'queries/header.json', 'queries/query_date.json',
              'queries/query_file.json', 'queries/query_text.json', 'queries/query_status.json']
requests_que = []
sub_time = {'0': 2629746, '1': 15778476, '2': 31556952, '3': 2629746}


def give_sub(user_id, user_id_client, sub_type):
    old_data = db_actions.get_eol(user_id_client)
    if db_actions.check_subscription(user_id_client):
        if sub_type != 3:
            db_actions.give_subscription(user_id_client, old_data[0] + sub_time[sub_type], sub_type)
        else:
            db_actions.give_subscription(user_id_client, old_data[0] + sub_time[sub_type], sub_type, old_data[1] + 30)
    else:
        if sub_type != 3:
            db_actions.give_subscription(user_id_client, time.time() + sub_time[sub_type], sub_type)
        else:
            db_actions.give_subscription(user_id_client, time.time() + sub_time[sub_type], sub_type, 30)
    bot.send_message(user_id, 'Операция успешно завершена')


def add_sub(user_id, sub_type):
    old_data = db_actions.get_eol(user_id)
    if db_actions.check_subscription(user_id):
        if sub_type != 3:
            db_actions.give_subscription(user_id, old_data[0] + sub_time[sub_type], sub_type)
        else:
            db_actions.give_subscription(user_id, old_data[0] + sub_time[sub_type], sub_type, old_data[1] + 30)
    else:
        if sub_type != 3:
            db_actions.give_subscription(user_id, time.time() + sub_time[sub_type], sub_type)
        else:
            db_actions.give_subscription(user_id, time.time() + sub_time[sub_type], sub_type, 30)


def get_notion_links(user_id, data):
    out = list()
    status = list()
    xyi = {}
    print(data)
    for i in data['results']:
        if i["object"] == "database":
            for g in i['properties'].keys():
                if i['properties'][g]['type'] == 'status':
                    for k in i['properties'][g]['status']['options']:
                        status.append([k['name'], k['color']])
                xyi.update({i['properties'][g]['type']: g})
            out.append([i['id'], i['title'][0]['plain_text'], i['url'], xyi, status])
            xyi = copy.deepcopy({})
    db_actions.update_notion_db(user_id, out)


def shorten_url(url):
    shortener = pyshorteners.Shortener()
    short_url = shortener.tinyurl.short(url)
    return short_url


def check_add_note(request, user_id):
    if request.status_code == 200:
        bot.send_message(user_id, f'<a href="{request.json()["url"]}">Заметка успешно добавлена!</a>', parse_mode='html')
    else:
        bot.send_message(user_id, 'Произошла ошибка при добавлении заметки, отсутствует поле в notion api')


def upload_photo(image, voice, video):
    if image is not None:
        photo_id = image[-1].file_id
        file_info = bot.get_file(photo_id)
        file_url = f"https://api.telegram.org/file/bot{config.get_config()['tg_api']}/{file_info.file_path}"
        return file_url
    elif voice is not None:
        file_id = voice.file_id
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{config.get_config()['tg_api']}/{file_info.file_path}"
        return shorten_url(file_url)
    else:
        video_id = video.file_id
        file_info = bot.get_file(video_id)
        file_url = f"https://api.telegram.org/file/bot{config.get_config()['tg_api']}/{file_info.file_path}"
        return shorten_url(file_url)


def url_redirect():
    app = Flask(__name__)
    @app.route('/')
    def get_parameters():
        # Get the value of the 'code' parameter from the URL
        code = request.args.get('code')
        requests_que.append(code)
        return redirect(f'{config.get_config()["tg_link"]}')
    app.run()


def add_to_query_addition_data(data, user_id, settings):
    for index, i in enumerate(temp_user_data.temp_data(user_id)[user_id][4]):
        if i is not None:
            if index == 0:
                date_json = json_requests.get_query(2)
                date_json['field']['date']['start'] = i
                date_json[db_actions.get_set_field_by_type(user_id,
                                                           settings[0],
                                                           'date')] = date_json['field']
                del date_json['field']
                data['properties'].update(date_json)
            elif index == 1:
                date_json = json_requests.get_query(5)
                date_json['field']['status']['name'] = i[0]
                date_json['field']['status']['color'] = i[1]
                date_json[db_actions.get_set_field_by_type(user_id,
                                                           settings[0],
                                                           'status')] = date_json['field']
                del date_json['field']
                data['properties'].update(date_json)
            temp_user_data.temp_data(user_id)[user_id][4][index] = None


def send_note(data, user_id, settings, headers):
    add_to_query_addition_data(data, user_id, settings)
    response = requests.post('https://api.notion.com/v1/pages', headers=headers,
                             json=data)
    check_add_note(response, user_id)
    print(response.json())


def eol_update(user_id):
    eol_data = db_actions.get_eol(user_id)
    if eol_data[2] == 3 and not db_actions.user_is_admin(user_id):
        db_actions.update_subscription_notes(user_id, eol_data[1]-1)



def main():
    @bot.message_handler(commands=['start', 'admin', 'change'])
    def start_msg(message):
        print(message)
        user_id = message.from_user.id
        buttons = Bot_inline_btns()
        command = message.text.replace('/', '')
        if command == 'start':
            if not db_actions.check_subscription(user_id):
                bot.send_message(user_id, 'Привет!\n'
                                          '<b>Я бот для моментальной отправки любого контента из Telegram в Notion.</b>\n\n'
                                          'Для начала, давай выберем чат из которого я буду отправлять контент в Notion.',
                                 parse_mode='HTML')
                bot.send_message(user_id, '🎁Лови <b>1 месяц премиум подписки бесплатно</b>, чтобы ты мог полноценно опробовать свои возможности', reply_markup=buttons.start_buttons(), parse_mode='HTML')
            else:
                bot.send_message(user_id, 'Привет!\n'
                                          '<b>Я бот для моментальной отправки любого контента из Telegram в Notion.</b>\n\n'
                                          'Для начала, давай выберем чат из которого я буду отправлять контент в Notion.',
                                 parse_mode='HTML', reply_markup=buttons.start_buttons())
            db_actions.add_user(user_id, message.from_user.first_name, message.from_user.last_name,
                                f'@{message.from_user.username}')
        elif command == 'change':
            bot.send_message(user_id, 'Здесь Вы можете изменить параметры для добавления заметок в Notion', reply_markup=buttons.choose_notion_dest())
        elif db_actions.user_is_admin(user_id):
            if command == 'admin':
                bot.send_message(user_id, 'Вы успешно зашли в админ-панель!', reply_markup=buttons.admin_btns())

    @bot.message_handler(content_types=['text', 'photo', 'voice', 'video'])
    def txt_msg(message):
        user_id = message.from_user.id
        user_caption = message.caption
        user_input = message.text
        user_photo = message.photo
        user_video = message.video
        user_voice = message.voice
        buttons = Bot_inline_btns()
        code = temp_user_data.temp_data(user_id)[user_id][0]
        if db_actions.user_is_existed(user_id):
            if db_actions.check_subscription(user_id):
                match code:
                    case 0:  # выдать лимит
                        if user_input is not None:
                            temp_user_data.temp_data(user_id)[user_id][1] = user_input
                            temp_user_data.temp_data(user_id)[user_id][0] = 3
                            bot.send_message(user_id, 'Что Вы хотите изменить?', reply_markup=buttons.actions_btns())
                        else:
                            bot.send_message(user_id, 'это не текст, попробуйте ещё раз')
                    case 1:  # выдать подписку
                        if user_input is not None:
                            temp_user_data.temp_data(user_id)[user_id][1] = user_input
                            temp_user_data.temp_data(user_id)[user_id][0] = 2
                            bot.send_message(user_id, 'Выберите тип подписки', reply_markup=buttons.cnt_btn())
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
                        try:
                            datetime.strptime(user_input, '%Y-%m-%d')
                            temp_user_data.temp_data(user_id)[user_id][0] = None
                            temp_user_data.temp_data(user_id)[user_id][4][0] = user_input
                            db_actions.update_authorized_status(user_id, True)
                            bot.send_message(user_id, 'Параметр успешно добавлен, можете оставить заметку или выбрать ещё один параметр')
                        except:
                            bot.send_message(user_id, 'Дата введена в неправильном формате, попробуйте ещё раз')
                    case _:
                        if db_actions.get_authorized_status(user_id):
                            try:
                                db_actions.update_authorized_status(user_id, False)
                                settings = db_actions.get_notion_settings(user_id)
                                headers = json_requests.get_query(1)
                                headers['Authorization'] = f'Bearer {db_actions.get_notion_access_token(user_id)}'
                                if settings[0] is not None and settings[1] is not None:
                                    types, names = zip(*db_actions.get_all_notion_fields_names(user_id, settings[0]).items())
                                    data = json_requests.get_query(0)
                                    data['parent']['database_id'] = db_actions.get_get_field_by_type(user_id, settings[0], 'id')
                                    if user_input is not None and (
                                            user_photo is None and user_video is None and user_voice is None):
                                        text_json = json_requests.get_query(4)
                                        text_json['field']['type'][0]['text']['content'] = user_input
                                        text_json['field'][types[settings[1]]] = text_json['field']['type']
                                        del text_json['field']['type']
                                        text_json[names[settings[1]]] = text_json['field']
                                        del text_json['field']
                                        data['properties'].update(text_json)
                                        send_note(data, user_id, settings, headers)
                                        eol_update(user_id)
                                    elif user_caption is not None and (
                                            user_photo is not None or user_video is not None or user_voice is not None):
                                        url = upload_photo(user_photo, user_voice, user_video)
                                        text_json = json_requests.get_query(4)
                                        text_json['field']['type'][0]['text']['content'] = user_caption
                                        text_json['field'][types[settings[1]]] = text_json['field']['type']
                                        del text_json['field']['type']
                                        text_json[names[settings[1]]] = text_json['field']
                                        del text_json['field']
                                        file_json = json_requests.get_query(3)
                                        file_json['field']['files'][0]['name'] = url
                                        file_json['field']['files'][0]['external']['url'] = url
                                        file_json[db_actions.get_set_field_by_type(user_id,
                                                                                   settings[0],
                                                                                   'files')] = file_json['field']
                                        del file_json['field']
                                        data['properties'].update(text_json)
                                        data['properties'].update(file_json)
                                        send_note(data, user_id, settings, headers)
                                        eol_update(user_id)
                                    elif user_input is None and (
                                            user_photo is not None or user_video is not None or user_voice is not None):
                                        url = upload_photo(user_photo, user_voice, user_video)
                                        file_json = json_requests.get_query(3)
                                        file_json['field']['files'][0]['name'] = url
                                        file_json['field']['files'][0]['external']['url'] = url
                                        file_json[db_actions.get_set_field_by_type(user_id,
                                                                                   settings[0],
                                                                                   'files')] = file_json['field']
                                        del file_json['field']
                                        data['properties'].update(file_json)
                                        send_note(data, user_id, settings, headers)
                                        eol_update(user_id)
                            except:
                                temp_user_data.temp_data(user_id)[user_id][4] = copy.deepcopy([None, None])
                                bot.send_message(user_id, 'Произошла ошибка, отсутствует нужное поле для записи, '
                                                          'добавьте его в Notion и произведите повторную авторизацию '
                                                          '/start')
                if user_input == 'написать заметку':
                    if db_actions.get_submit_mods(user_id):
                        bot.send_message(user_id, 'Что вы хотите добавить?', reply_markup=buttons.additions_btns())
                    else:
                        db_actions.update_authorized_status(user_id, True)
                        bot.send_message(user_id, 'Отправьте заметку (фото, видео, текст, голосовое)')

            else:
                bot.send_message(user_id,
                                 'Сначала нужно настроить параметры для добавления заметок в Notion',
                                 reply_markup=buttons.choose_notion_dest())

    @bot.callback_query_handler(func=lambda call: True)
    def callback(call):
        user_id = call.message.chat.id
        buttons = Bot_inline_btns()
        if db_actions.user_is_existed(user_id):
            code = temp_user_data.temp_data(user_id)[user_id][0]
            if call.data == 'sub':
                subsc = db_actions.get_eol(user_id)
                if subsc[2] == 3:
                    bot.send_message(user_id, 'Выберите подписку!\n\n'
                                              f'Ваша подписка доступна до: {datetime.utcfromtimestamp(subsc[0]).strftime("%Y-%m-%d %H:%M")}\n Заметок осталось: {subsc[1]}',
                                     reply_markup=buttons.payment_btn())
                else:
                    bot.send_message(user_id, 'Выберите подписку!\n\n'
                                              f'Ваша подписка доступна до: {datetime.utcfromtimestamp(subsc[0]).strftime("%Y-%m-%d %H:%M")}',
                                     reply_markup=buttons.payment_btn())
            if call.data[:12] == 'subscription':
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
            if db_actions.check_subscription(user_id):
                if db_actions.user_is_admin(user_id):
                    if call.data == 'givelimit':
                        temp_user_data.temp_data(user_id)[user_id][0] = 0
                        bot.send_message(user_id,
                                         'Введите <i><b>ID пользователя</b></i>, которому нужно выдать лимит',
                                         parse_mode='HTML')
                    elif call.data == 'givesub':
                        temp_user_data.temp_data(user_id)[user_id][0] = 1
                        bot.send_message(user_id,
                                         'Введите <i><b>ID пользователя</b></i>, которому нужно выдать подписку',
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
                if call.data == 'done':
                    flag = False
                    for code in requests_que:
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
                            "code": code,
                            "redirect_uri": config.get_config()['notion_redirect_uri']
                        }
                        # Отправьте запрос на сервер авторизации Notion
                        r = requests.post("https://api.notion.com/v1/oauth/token", headers=headers, json=body)
                        print(r.json())
                        if r.status_code == 200:
                            requests_que.remove(code)
                            flag = True
                            break
                    if flag:
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
                        get_notion_links(user_id, response.json())
                        bot.send_message(user_id,
                                         'Авторизация успешна! Теперь нужно настроить параметры для добавления '
                                         'заметок в Notion',
                                         reply_markup=buttons.choose_notion_dest())
                    else:
                        bot.send_message(user_id, '<b>Авторизация не пройдена!</b>\n\n'
                                                  'Попробуйте еще раз!', parse_mode='HTML')
                elif call.data[:13] == 'choose_status':
                    settings = db_actions.get_notion_settings(user_id)
                    data = db_actions.get_get_field_by_type(user_id, settings[0], 'db_status')
                    temp_user_data.temp_data(user_id)[user_id][0] = None
                    temp_user_data.temp_data(user_id)[user_id][4][1] = data[int(call.data[13:])]
                    db_actions.update_authorized_status(user_id, True)
                    bot.send_message(user_id,
                                     'Параметр успешно добавлен, можете оставить заметку или выбрать ещё один параметр')
                elif call.data[:11] == 'notions_dbs':
                    db_actions.update_notion_settings(True, int(call.data[11:]), user_id)
                    auto_index = db_actions.auto_select_field(user_id, int(call.data[11:]))
                    db_actions.update_notion_settings(False, auto_index, user_id)
                    bot.send_message(user_id, 'Операция совершена успешно', reply_markup=buttons.write_note())
                elif call.data[:10] == 'select_dst':
                    match call.data[10:]:
                        case '0':
                            names = db_actions.get_all_notion_db_names(user_id)
                            bot.send_message(user_id, 'Выберите базу данных', reply_markup=buttons.notion_db_btns(names))
                        case '1':
                            bot.send_message(user_id, 'Какой режим добавления заметок вы хотите использовать?', reply_markup=buttons.mods_btns())
                elif call.data[:10] == 'change_mod':
                    match call.data[10:]:
                        case '0':
                            db_actions.change_submit_mod(False, user_id)
                            bot.send_message(user_id, 'Операция совершена успешно')
                        case '1':
                            db_actions.change_submit_mod(True, user_id)
                            bot.send_message(user_id, 'Операция совершена успешно')
                elif call.data[:12] == 'add_addition':
                    match call.data[12:]:
                        case '0':
                            temp_user_data.temp_data(user_id)[user_id][0] = 6
                            bot.send_message(user_id, 'Введите дату в формате (2024-05-01)')
                        case '1':
                            settings = db_actions.get_notion_settings(user_id)
                            data = db_actions.get_get_field_by_type(user_id, settings[0], 'db_status')
                            bot.send_message(user_id, 'Выберите статус', reply_markup=buttons.choose_statis(data))

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
    json_requests = RequestsParser(json_paths)
    temp_user_data = TempUserData()
    db = DB(config.get_config()['db_file_name'], Lock())
    db_actions = DbAct(db, config, config.get_config()['xlsx_path'])
    threading.Thread(target=url_redirect).start()
    ssh_tunnel = ngrok.connect("5000", "http")
    print(ssh_tunnel)
    bot = telebot.TeleBot(config.get_config()['tg_api'])
    main()
