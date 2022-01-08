from .db import DB
from .setting import setting
import random
import nltk 
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.svm import LinearSVC


def filter_text(text):
    text = text.lower()
    text = [c for c in text if c not in str(setting['FILTER'])]
    text = ''.join(text)
    return text

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
            dictionary.append([filter_text(row['question']), row['response']])

        qa_by_word_dataset = {}

        for question, answer in dictionary:
            words = question.split(' ')
            for word in words:
                if word not in qa_by_word_dataset:
                    qa_by_word_dataset[word] = []
                qa_by_word_dataset[word].append((question, answer))

        qa_by_word_dataset = {word: qa_list for word, qa_list in qa_by_word_dataset.items() if len(qa_list) < 1000}

        return qa_by_word_dataset
    else:
        return None

def fill_template(ls_words):
    db = DB()

    where = "WHERE 1 = 0"
    for word_ls_words in ls_words:
        where = where + " or question like '%{0}%'".format(word_ls_words)

    dt = db.exec('''
        Select question, response from Template {0};
    '''.format(where))
    
    dictionary = []

    for row in dt.table:
        dictionary.append([filter_text(row['question']), row['response']])

    qa_by_word_dataset = {}

    for question, answer in dictionary:
        words = question.split(' ')
        for word in words:
            if word not in qa_by_word_dataset:
                qa_by_word_dataset[word] = []
            qa_by_word_dataset[word].append((question, answer))

    qa_by_word_dataset = {word: qa_list for word, qa_list in qa_by_word_dataset.items() if len(qa_list) < 1000}

    return qa_by_word_dataset

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
    if dialog:
        text = filter_text(text)
        # -----------------------------------------
        # Получение ответа из диалогов
        # -----------------------------------------
        words = text.split(' ')

        qa = []
        for word in words:
            if word in dialog:
                qa += dialog[word]
        qa = list(set(qa))[:setting['MAX_W']]

        results = []

        for question, answer in qa:
            dist = nltk.edit_distance(question, text)
            dist_percent = dist / len(question)
            results.append([dist_percent, question, answer])

        if results:
            dist_percent, question, answer = min(results, key=lambda pair:pair[0])
            if dist_percent <= setting['DIST']:
                return answer
    else:
        return

def get_answer_template(text):
    # -----------------------------------------
    # Получение ответа из таблицы шаблонов
    # -----------------------------------------
    list_w = filter_text(text).split(' ')
    template = fill_template(list_w)
    if template:
        text = filter_text(text)
        # -----------------------------------------
        # Получение ответа из диалогов
        # -----------------------------------------
        words = text.split(' ')

        qa = []
        for word in words:
            if word in template:
                qa += template[word]
        qa = list(set(qa))[:setting['MAX_W']]

        results = []

        for question, answer in qa:
            dist = nltk.edit_distance(question, text)
            dist_percent = dist / len(question)
            results.append([dist_percent, question, answer])

        if results:
            dist_percent, question, answer = min(results, key=lambda pair:pair[0])
            if dist_percent <= setting['DIST']:
                return answer
    else:
        return


    
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
