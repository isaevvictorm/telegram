import sqlite3
import os
import traceback
import zipfile

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
        if not os.path.exists(os.path.join(os.getcwd() + '/database/database.db')):
            with zipfile.ZipFile(os.path.join(os.getcwd() + '/database/database.zip'), 'r') as zip_ref:
                zip_ref.extractall(os.path.join(os.getcwd() + '/database/'))

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
