import json
import os
import requests
from .db import DB

class Setting:

    setting = None

    def __init__(self):
            try:
                with open(os.path.join(os.getcwd() + "/", "config.json")) as f:
                    self.setting = json.load(f)
            except Exception as ee:
                print("Error: ({0})".format(str(ee)))
            
            db = DB()
            dt = db.exec('''
                Select name, value from Setting
            ''')

            for key in self.setting:
                if self.setting[key] not in [row['name'] for row in dt.table]:
                    if key == 'WEBHOOK_HOST':
                        db.exec('''
                            INSERT INTO Setting (name, value, type, description)
                            Select
                                '{0}' as name,
                                '{1}' as value,
                                'text' as type,
                                'IP для WebHook (по умолчанию 127.0.0.1)' as description
                            WHERE NOT EXISTS (SELECT * FROM Setting WHERE name = '{0}');
                        '''.format("WEBHOOK_HOST", self.setting["WEBHOOK_HOST"]))
                    
                    elif key == 'WEBHOOK_PORT': 
                        db.exec('''
                            INSERT INTO Setting (name, value, type, description)
                            Select
                                '{0}' as name,
                                '{1}' as value,
                                'text' as type,
                                'Порт для WebHook (по умолчанию 8443)' as description
                            WHERE NOT EXISTS (SELECT * FROM Setting WHERE name = '{0}');
                        '''.format("WEBHOOK_PORT", self.setting["WEBHOOK_PORT"]))

                    elif key == 'DOMAIN':
                        db.exec('''
                            INSERT INTO Setting (name, value, type, description)
                            Select
                                '{0}' as name,
                                '{1}' as value,
                                'text' as type,
                                'Домен для адмники' as description
                            WHERE NOT EXISTS (SELECT * FROM Setting WHERE name = '{0}');
                        '''.format("DOMAIN", self.setting["DOMAIN"]))
                    
                    elif key == 'TOKEN':
                        db.exec('''
                            INSERT INTO Setting (name, value, type, description)
                            Select
                                '{0}' as name,
                                '{1}' as value,
                                'text' as type,
                                'Токен бота из @BotFather' as description
                            WHERE NOT EXISTS (SELECT * FROM Setting WHERE name = '{0}');
                        '''.format("TOKEN", self.setting["TOKEN"]))

                    elif key == 'AMDIN':
                        db.exec('''
                            INSERT INTO Setting (name, value, type, description)
                            Select
                                '{0}' as name,
                                '{1}' as value,
                                'text' as type,
                                'ID администратора бота' as description
                            WHERE NOT EXISTS (SELECT * FROM Setting WHERE name = '{0}');
                        '''.format("AMDIN", self.setting["AMDIN"]))
                    
                    elif key == 'DIST':
                        db.exec('''
                            INSERT INTO Setting (name, value, type, description)
                            Select
                                '{0}' as name,
                                '{1}' as value,
                                'float' as type,
                                'Процент совпадения для диалогов (если они есть)' as description
                            WHERE NOT EXISTS (SELECT * FROM Setting WHERE name = '{0}');
                        '''.format("DIST", self.setting["DIST"]))
                    
                    elif key == 'PROBA':
                        db.exec('''
                            INSERT INTO Setting (name, value, type, description)
                            Select
                                '{0}' as name,
                                '{1}' as value,
                                'float' as type,
                                'Процент совпадения для интентов (база знаний)' as description
                            WHERE NOT EXISTS (SELECT * FROM Setting WHERE name = '{0}');
                        '''.format("PROBA", self.setting["PROBA"]))
                    
                    elif key == 'NORM':
                        db.exec('''
                            INSERT INTO Setting (name, value, type, description)
                            Select
                                '{0}' as name,
                                '{1}' as value,
                                'float' as type,
                                'Процент совпадения для добаления вопроса в интент (базу знаний)' as description
                            WHERE NOT EXISTS (SELECT * FROM Setting WHERE name = '{0}');
                        '''.format("NORM", self.setting["NORM"]))
                    
                    elif key == 'MAX_W':
                        db.exec('''
                            INSERT INTO Setting (name, value, type, description)
                            Select
                                '{0}' as name,
                                '{1}' as value,
                                'int' as type,
                                'Максимальный повтор слов в словарях (исключаем местоимения, союзы и т.п.)' as description
                            WHERE NOT EXISTS (SELECT * FROM Setting WHERE name = '{0}');
                        '''.format("MAX_W", self.setting["MAX_W"]))
                    
                    elif key == 'CNT_MESSAGE_IN_CHAT':
                        db.exec('''
                            INSERT INTO Setting (name, value, type, description)
                            Select
                                '{0}' as name,
                                '{1}' as value,
                                'int' as type,
                                'Длина чатов опертора системы' as description
                            WHERE NOT EXISTS (SELECT * FROM Setting WHERE name = '{0}');
                        '''.format("CNT_MESSAGE_IN_CHAT", self.setting["CNT_MESSAGE_IN_CHAT"]))


                    elif key == 'FILTER':
                        db.exec('''
                            INSERT INTO Setting (name, value, type, description)
                            Select
                                '{0}' as name,
                                '{1}' as value,
                                'text' as type,
                                'Фильтр символов' as description
                            WHERE NOT EXISTS (SELECT * FROM Setting WHERE name = '{0}');
                        '''.format("FILTER", self.setting["FILTER"]))
                    elif key == 'SEND_PLUG_TO_CHAT':
                        db.exec('''
                            INSERT INTO Setting (name, value, type, description)
                            Select
                                '{0}' as name,
                                '{1}' as value,
                                'int' as type,
                                'Отправлять заглушки в чаты (0 - нет; 1 - да)' as description
                            WHERE NOT EXISTS (SELECT * FROM Setting WHERE name = '{0}');
                        '''.format("SEND_PLUG_TO_CHAT", self.setting["SEND_PLUG_TO_CHAT"]))
                    
                    else:
                        db.exec('''
                            INSERT INTO Setting (name, value, type, description)
                            Select
                                '{0}' as name,
                                '{1}' as value,
                                'text' as type,
                                '{0}' as description
                            WHERE NOT EXISTS (SELECT * FROM Setting WHERE name = '{0}');
                        '''.format(key, self.setting[key]))

    def get(self):
        db = DB()
        dt = db.exec('''
            Select name, value, type from Setting;
        ''')
        for row in dt.table:
            if row['type'] == 'int':
                self.setting[row['name']] = int(row['value'])
            elif row['type'] == 'float':
                self.setting[row['name']] = float(row['value'])
            else:
                self.setting[row['name']] = str(row['value'])
        
        return self.setting
            
            
            


