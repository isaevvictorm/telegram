
from .db import DB
from .setting import setting
import random
import nltk 

def fill_dialog():
    db = DB()
    dt = db.exec('''
        SELECT name FROM sqlite_master WHERE type='table' AND name='Dialog';
    ''')

    if len(dt.table) > 0:
        dt = db.exec('''
            Select question, response from Dialog;
        ''')
        
        dictionary = []

        for row in dt.table:
            dictionary.append([row['question'], row['response']])

        return dictionary
    else:
        return []

dialog = fill_dialog()

def get_answer_intent(text):
    # -----------------------------------------
    # Получение ответа из таблицы классификации
    # -----------------------------------------

    return

def get_answer_failure():
    # -----------------------------------------
    # Получение ответа из таблицы заглушек
    # -----------------------------------------
    db = DB()
  
    dt = db.exec('''
        Select text from Failure;
    ''')
    
    dictionary = []

    for row in dt.table:
        dictionary.append(row['text'])

    if len(dictionary) == 0:
        return
    else:
        return random.sample(dictionary, 1)[0]


def get_answer_dialog(text):
    if len(dialog) > 0:
        # -----------------------------------------
        # Получение ответа из диалогов
        # -----------------------------------------
        for question, answer in dialog:
            dist = nltk.edit_distance(text, question)
            if dist / len(text) < setting['DIST']:
                return answer
    else:
        return

def get_answer_template(text):
    # -----------------------------------------
    # Получение ответа из таблицы шаблонов
    # -----------------------------------------
    
    return

def generate_answer(text):

    answer = get_answer_intent(text)
    if answer:
        return answer

    answer = get_answer_template(text)
    if answer:
        return answer

    answer = get_answer_dialog(text)
    if answer:
        return answer

    answer = get_answer_failure()
    if answer:
        return answer
    
    return "Ожидайте, я ищу ответ на Ваше сообщение..."
