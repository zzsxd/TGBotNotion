import telebot
from frontend import Bot_inline_btns
from db import DB
from backend import TempUserData, DbAct
from config_parser import ConfigParser
import os
from threading import Lock
import platform
import json

config_name = 'secrets.json'


def main():
    @bot.message_handler(commands=['start'])
    def start_msg(message):
        user_id = message.chat.id
        buttons = Bot_inline_btns()
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
            if call.back == 'property':
                bot.send_message(user_id, 'зачем кликаешь тут еще ниче не работает')
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