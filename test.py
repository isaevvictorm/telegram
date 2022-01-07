import os
import io
import sqlite3
import traceback

class DBResult:

    def __init__(self, result, row_count, table, columns, err, column_description):
        self.result=result
        self.row_count=row_count
        self.table = table
        self.columns=columns
        self.column_description = column_description
        self.err = err

class DB:

    def __init__(self):
        if not os.path.exists(os.path.join(os.getcwd() + '/database/')):
            os.makedirs(os.path.join(os.getcwd() + '/database/'))

    def exec(self, query):
        try:
            with sqlite3.connect(os.path.join(os.getcwd() + '/database/', "database.db")) as conn:
                cursor = conn.cursor()
                lst=[]
                cursor.execute(query)
                try:
                    row = cursor.fetchone()
                    if cursor.description:
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
                    else:
                        return  DBResult(True,cursor.rowcount,[],[],None,None)
                except sqlite3.Error as ee:
                    if str(ee).lower().find('already') == -1 and str(ee).lower().find('duplicate') == -1:
                        conn.commit()
                        return  DBResult(True,cursor.rowcount,[],[],None,None)
                    else:
                        return  DBResult(False,0,[],[],str(traceback.format_exc()),None)
                except Exception as ee:
                    return  DBResult(False,0,[],[],str(traceback.format_exc()),None)
        except Exception as ee:
            return DBResult(False,0,[],[],str(traceback.format_exc()),None)

db = DB()

db.exec('''
    CREATE TABLE "Dialog" (
        id_template INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        response TEXT,
        flag_correct INTEGER default 1,
        date_insert datetime default current_timestamp
    );
''')

dt = db.exec('''
    Select count(*) as cnt from Dialog;
''')
print('Count:', dt.table[0]['cnt'])
if str(dt.table[0]['cnt']) == '0':

    mass = []

    with io.open(os.path.join(os.getcwd() + "/startup/dialogues.txt"), newline='', encoding="utf-8", errors='replace') as f:
        content = f.read()
        for replicas in [dialogue_line.split('\n') for dialogue_line in content.split('\n\n')]:
            if len(replicas) < 2:
                continue
            
            question, answer = replicas[:2]
            question = question[2:]
            answer = answer[2:]

            db.exec('''
                INSERT INTO Dialog (question, response) values ('{0}', '{1}');
            '''.format(question, answer))

   