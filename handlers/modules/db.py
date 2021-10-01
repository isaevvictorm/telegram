import sqlite3
import os
from .setting import setting

def get_database():
    try:
        if not os.path.exists(os.path.join(os.getcwd() + '/database/')):
            os.makedirs(os.path.join(os.getcwd() + '/database/'))
        conn = sqlite3.connect(os.path.join(os.getcwd() + '/database/', "system.db"))
        cursor = conn.cursor()
        cursor.execute("""
            Select token from Webhook where status = 1;
        """)
        records = cursor.fetchall()
        if len(records) > 0:
            return records[0][0]
        else:
            return 'system'
    except sqlite3.Error as e:
        if str(e).lower().find('already') == -1 and str(e).lower().find('duplicate') == -1:
            print('Error DB: ' + str(e))
        return 'system'

def execute(query, system = None):
    try:
        if not os.path.exists(os.path.join(os.getcwd() + '/database/')):
            os.makedirs(os.path.join(os.getcwd() + '/database/'))
        conn = sqlite3.connect(os.path.join(os.getcwd() + '/database/', "{0}.db".format('system' if system else str(get_database()).split(':')[1])))
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
            print('Error DB: ' + str(e))
        return None

def executescript(query, system = None):
    try:
        if not os.path.exists(os.path.join(os.getcwd() + '/database/')):
            os.makedirs(os.path.join(os.getcwd() + '/database/'))
        conn = sqlite3.connect(os.path.join(os.getcwd() + '/database/', "{0}.db".format('system' if system else str(get_database()).split(':')[1])))
        cursor = conn.cursor()
        cursor.executescript("""
            BEGIN TRANSACTION;

            {0}

            COMMIT;
        """.format(query))
        records = cursor.fetchall()
        if len(records) > 0:
            return records
        else:
            return None
    except sqlite3.Error as e:
        if str(e).lower().find('already') == -1 and str(e).lower().find('duplicate') == -1:
            print('Error DB: ' + str(e))
        return None
