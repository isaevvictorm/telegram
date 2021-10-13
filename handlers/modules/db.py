import sqlite3
import os
from .setting import setting
import traceback


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
            return 'debug'
    except sqlite3.Error as e:
        if str(e).lower().find('already') == -1 and str(e).lower().find('duplicate') == -1:
            print('Error DB: ' + str(e))
        return 'debug'

class DBResult:

    def __init__(self, result, row_count, table, columns, err, column_description):
        self.result=result
        self.row_count=row_count
        self.table = table
        self.columns=columns
        self.column_description = column_description
        self.err = err

class DB:

    system = None

    def __init__(self, system = None):
        self.system = system
        if not os.path.exists(os.path.join(os.getcwd() + '/database/')):
            os.makedirs(os.path.join(os.getcwd() + '/database/'))

    def exec(self, query):
        try:
            with sqlite3.connect(os.path.join(os.getcwd() + '/database/', "{0}.db".format('system' if self.system else str(setting['TOKEN']).split(':')[0]))) as conn:
                cursor = conn.cursor()
                lst=[]
                cursor.execute(query)
                try:
                    row = cursor.fetchone()
                    columns = [column[0] for column in cursor.description]
                    column_d = cursor.description
                    while row:
                        row_dct=dict()
                        for i in range(0,len(row)):
                            row_dct.update({columns[i]:row[i]})
                        lst.append(row_dct)
                        row = cursor.fetchone()
                    if not lst:
                        return DBResult(True,cursor.rowcount,[],columns,None,column_d)
                    return  DBResult(True,cursor.rowcount,lst,columns,None,column_d)
                except sqlite3.Error as ee:
                    if str(e).lower().find('already') == -1 and str(e).lower().find('duplicate') == -1:
                        conn.commit()
                        return  DBResult(True,cursor.rowcount,[],[],None,None)
                    else:
                        return  DBResult(False,0,[],[],str(traceback.format_exc()),None)
                except Exception as ee:
                    return  DBResult(False,0,[],[],str(traceback.format_exc()),None)
        except Exception as e:
            return DBResult(False,0,[],[],str(traceback.format_exc()),None)

def execute(query, system = None):
    try:
        if not os.path.exists(os.path.join(os.getcwd() + '/database/')):
            os.makedirs(os.path.join(os.getcwd() + '/database/'))
        conn = sqlite3.connect(os.path.join(os.getcwd() + '/database/', "{0}.db".format('system' if system else str(get_database()).split(':')[0])))
        cursor = conn.cursor()
        cursor.execute("""
            {0}
        """.format(query))
        records = cursor.fetchall()
        if len(records) > 0:
            return records
        else:
            return []
    except sqlite3.Error as e:
        if str(e).lower().find('already') == -1 and str(e).lower().find('duplicate') == -1:
            print('Error DB: ' + str(e))
            print(query)
        return []

def executescript(query, system = None):
    try:
        if not os.path.exists(os.path.join(os.getcwd() + '/database/')):
            os.makedirs(os.path.join(os.getcwd() + '/database/'))
        conn = sqlite3.connect(os.path.join(os.getcwd() + '/database/', "{0}.db".format('system' if system else str(get_database()).split(':')[0])))
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
            return []
    except sqlite3.Error as e:
        if str(e).lower().find('already') == -1 and str(e).lower().find('duplicate') == -1:
            print('Error DB: ' + str(e))
        return []
