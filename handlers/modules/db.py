import sqlite3
import os
from .setting import setting

def sql_exec(query):
    try:
        if not os.path.exists(os.path.join(os.getcwd() + '/database/')):
            os.makedirs(os.path.join(os.getcwd() + '/database/'))
        conn = sqlite3.connect(os.path.join(os.getcwd() + '/database/', "{0}.db".format(str(setting['BOT']['TOKEN']).split(':')[0])))
        cursor = conn.cursor()
        cursor.execute("""
            {0}
        """.format(query))
        records = cursor.fetchall()
        if len(records) > 0:
            return records
        else:
            return None
    except sqlite3.Error as e:
        if str(e).lower().find('already') == -1 and str(e).lower().find('duplicate') == -1:
            print('Ошибка БД: ' + str(e))
        return None
