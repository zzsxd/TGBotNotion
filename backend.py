import os
import datetime
import time
import json
import pandas as pd
from openpyxl import load_workbook


class TempUserData:
    def __init__(self):
        super(TempUserData, self).__init__()
        self.__user_data = {}

    def temp_data(self, user_id):
        if user_id not in self.__user_data.keys():
            self.__user_data.update({user_id: [None, None, None, None, [None, None], True, None]})
        return self.__user_data


class DbAct:
    def __init__(self, db, config, path_xlsx):
        super(DbAct, self).__init__()
        self.__db = db
        self.__config = config
        self.__fields = ['ID пользователя', 'Nickname пользователя', 'Дата регистрации', 'Лимит запросов', 'Дата действия подпики',]
        self.__dump_path_xlsx = path_xlsx

    def add_user(self, user_id, first_name, last_name, nick_name):
        if not self.user_is_existed(user_id):
            if user_id in self.__config.get_config()['admins']:
                is_admin = True
            else:
                is_admin = False
            self.__db.db_write(
                'INSERT INTO users (user_id, first_name, last_name, nick_name, is_admin, exp_date, notes_count, subscription_type, notion_settings, notion_token, db_info, submit_mod, date_registration) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (user_id, first_name, last_name, nick_name, is_admin, time.time()+2592000, 30, 3, json.dumps([None, None], ensure_ascii=False), '', '', False, datetime.datetime.now()))

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

    def update_subscription_time(self, user_id, times):
        self.__db.db_write('UPDATE users SET exp_date = ? WHERE user_id = ?', (times, user_id))

    def update_subscription_notes(self, user_id, notes_count):
        self.__db.db_write('UPDATE users SET notes_count = ? WHERE user_id = ?', (notes_count, user_id))

    def give_subscription(self, user_id, date, sub_type, notes=0):
        if notes == 0:
            self.__db.db_write('UPDATE users SET exp_date = ?, subscription_type = ? WHERE user_id = ?', (date, sub_type, user_id))
        else:
            self.__db.db_write('UPDATE users SET exp_date = ?, subscription_type = ?, notes_count = ? WHERE user_id = ?',
                               (date, sub_type, notes, user_id))

    def update_notion_token(self, notion_token, user_id):
        self.__db.db_write('UPDATE users SET notion_token = ? WHERE user_id = ?', (notion_token, user_id))

    def update_notion_db(self, user_id, data):
        self.__db.db_write('UPDATE users SET db_info = ? WHERE user_id = ?', (json.dumps(data, ensure_ascii=False), user_id))

    def get_notion_access_token(self, user_id):
        return self.__db.db_read('SELECT notion_token FROM users WHERE user_id = ?', (user_id, ))[0][0]

    def update_authorized_status(self, user_id, data):
        self.__db.db_write('UPDATE users SET authorized = ? WHERE user_id = ?', (data, user_id))

    def get_authorized_status(self, user_id):
        data = self.__db.db_read('SELECT authorized FROM users WHERE user_id = ?', (user_id, ))
        if len(data) > 0:
            if data[0][0] == 1:
                status = True
            else:
                status = False
            return status

    def change_submit_mod(self, switch, user_id):
        self.__db.db_write('UPDATE users SET submit_mod = ? WHERE user_id = ?', (switch, user_id))

    def get_submit_mods(self, user_id):
        data = self.__db.db_read('SELECT submit_mod FROM users WHERE user_id = ?', (user_id,))
        if len(data) > 0:
            if data[0][0] == 1:
                status = True
            else:
                status = False
            return status

    def get_notion_settings(self, user_id):
        return json.loads(self.__db.db_read('SELECT notion_settings FROM users WHERE user_id = ?', (user_id, ))[0][0])

    def update_notion_settings(self, switch, settings, user_id):
        data = self.get_notion_settings(user_id)
        if switch:
            data[0] = settings
        else:
            data[1] = settings
        self.__db.db_write('UPDATE users SET notion_settings = ? WHERE user_id = ?', (json.dumps(data, ensure_ascii=False), user_id))

    def get_notion_db(self, user_id):
        data = self.__db.db_read('SELECT db_info FROM users WHERE user_id = ?', (user_id, ))
        if len(data) > 0:
            return json.loads(data[0][0])

    def get_all_notion_db_names(self, user_id):
        data = self.get_notion_db(user_id)
        names = list()
        for i in data:
            names.append(i[1])
        return names

    def auto_select_field(self, user_id, db_index):
        data = self.get_notion_db(user_id)
        for index, g in enumerate(data[db_index][3].keys()):
            if g in ['title']:
                return index

    def get_not_all_notion_fields_names(self, user_id, db_index):
        out = dict()
        data = self.get_notion_db(user_id)
        for i, g in data[db_index][3].items():
            if i in ['title', 'rich_text']:
                out.update({i: g})
        return out

    def get_all_notion_fields_names(self, user_id, db_index):
        out = dict()
        data = self.get_notion_db(user_id)
        for i, g in data[db_index][3].items():
            out.update({i: g})
        return out

    def get_get_field_by_type(self, user_id, db_index, user_search):
        search = {'id': 0, 'db_name': 1, 'db_link': 2, 'db_fields': 3, 'db_status': 4}
        data = self.get_notion_db(user_id)
        return data[db_index][search[user_search]]

    def get_set_field_by_type(self, user_id, db_index, field_type):
        data = self.get_notion_db(user_id)
        return data[db_index][3][field_type]

    def read_user(self):
        return self.__db.db_read('SELECT user_id FROM users', ())

    def read_row(self):
        return self.__db.db_read('SELECT COUNT(*) FROM users', ())[0][0]


    def db_export_xlsx(self):
        d = {'ID пользователя': [], 'Nickname пользователя': [], 'Дата регистрации': [], 'Лимит запросов': [], 'Дата действия подпики': [],}
        users = self.__db.db_read('SELECT user_id, nick_name, date_registration, notes_count, exp_date FROM users', ())
        if len(users) > 0:
            for user in users:
                for info in range(len(list(user))):
                    if info == 4:
                        d[self.__fields[info]].append(datetime.datetime.fromtimestamp(user[info]).strftime('%Y-%m-%d %H:%M:%S'))
                    else:
                        d[self.__fields[info]].append(user[info])
            df = pd.DataFrame(d)
            df.to_excel(self.__config.get_config()['xlsx_path'], sheet_name='пользователи', index=False)