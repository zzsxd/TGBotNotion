
import os
import time
import json
import csv

class TempUserData:
    def __init__(self):
        super(TempUserData, self).__init__()
        self.__user_data = {}

    def temp_data(self, user_id):
        if user_id not in self.__user_data.keys():
            self.__user_data.update({user_id: [None, None, None]})
        return self.__user_data


class DbAct:
    def __init__(self, db, config, path_xlsx):
        super(DbAct, self).__init__()
        self.__db = db
        self.__config = config
        self.__fields = ['Имя', 'Фамилия', 'Никнейм', 'Номер телефона']
        self.__dump_path_xlsx = path_xlsx

    def add_user(self, user_id, first_name, last_name, nick_name):
        if not self.user_is_existed(user_id):
            if user_id in self.__config.get_config()['admins']:
                is_admin = True
            else:
                is_admin = False
            self.__db.db_write(
                'INSERT INTO users (user_id, first_name, last_name, nick_name, is_admin, exp_date, notes_count, subscription_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (user_id, first_name, last_name, nick_name, is_admin, time.time()+2592000, 30, 3))

    def user_is_existed(self, user_id):
        data = self.__db.db_read('SELECT count(*) FROM users WHERE user_id = ?', (user_id,))
        if len(data) > 0:
            if data[0][0] > 0:
                status = True
            else:
                status = False
            return status

    def user_is_admin(self, user_id):
        data = self.__db.db_read('SELECT is_admin FROM users WHERE user_id = ?', (user_id,))
        if len(data) > 0:
            if data[0][0] == 1:
                status = True
            else:
                status = False
            return status

    def check_subscription(self, user_id):
        data = self.__db.db_read('SELECT exp_date, notes_count, subscription_type FROM users WHERE user_id = ?', (user_id,))
        if len(data) > 0:
            if data[0][0] > time.time() and data[0][1] > 0:
                if data[0][2] == 3 and data[0][1] > 0:
                    return True
                elif data[0][2] != 3:
                    return True
            elif self.user_is_admin(user_id):
                return True

    def get_eol(self, user_id):
        return self.__db.db_read('SELECT exp_date, notes_count, subscription_type FROM users WHERE user_id = ?', (user_id, ))[0]

    def update_subscription_time(self, user_nick, times):
        self.__db.db_write('UPDATE users SET exp_date = ? WHERE nick_name = ?', (times, user_nick))

    def update_subscription_notes(self, user_nick, notes_count):
        self.__db.db_write('UPDATE users SET notes_count = ? WHERE nick_name = ?', (notes_count, user_nick))

    def give_subscription(self, nick_name, date, sub_type, notes=0):
        if notes == 0:
            self.__db.db_write('UPDATE users SET exp_date = ?, subscription_type = ? WHERE nick_name = ?', (date, sub_type, nick_name))
        else:
            self.__db.db_write('UPDATE users SET exp_date = ?, subscription_type = ?, notes_count = ? WHERE nick_name = ?',
                               (date, sub_type, notes, nick_name))

    def give_subscription_ud(self, user_id, date, sub_type, notes=0):
        if notes == 0:
            self.__db.db_write('UPDATE users SET exp_date = ?, subscription_type = ? WHERE user_id = ?', (date, sub_type, user_id))
        else:
            self.__db.db_write('UPDATE users SET exp_date = ?, subscription_type = ?, notes_count = ? WHERE user_id = ?',
                               (date, sub_type, notes, user_id))

    def update_notion_token(self, notion_token, user_id):
        self.__db.db_write('UPDATE users SET notion_token = ? WHERE user_id = ?', (notion_token, user_id))

    def update_notion_db(self, user_id, data):
        self.__db.db_write('UPDATE users SET db_info = ? WHERE user_id = ?', (json.dumps(data), user_id))

    def get_notion_db(self, user_id):
        data = self.__db.db_read('SELECT db_info FROM users WHERE user_id = ?', (user_id, ))
        if len(data) > 0:
            return json.loads(data[0][0])

    def get_db_notion_id(self, user_id, db_name):
        data = self.__db.db_read('SELECT db_info FROM users WHERE user_id = ?', (user_id, ))[0][0]
        data = json.loads(data)
        for i in data:
            if i[1] == db_name:
                return i[0]