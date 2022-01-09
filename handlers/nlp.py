from .modules import DB, setting
import random
import nltk 
from concurrent.futures import ThreadPoolExecutor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from aiohttp import web
from .modules import setting
import asyncio

async def do(func, arg_obj):
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers = 100)
    return await loop.run_in_executor(executor, func, arg_obj)

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

        qa_by_word_dataset = {word: qa_list for word, qa_list in qa_by_word_dataset.items() if len(qa_list) < setting['MAX_W']}

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

    qa_by_word_dataset = {word: qa_list for word, qa_list in qa_by_word_dataset.items() if len(qa_list) < setting['MAX_W']}

    return qa_by_word_dataset

def fill_intent():
    x_temp = []
    y_temp = []
    
    db = DB()
    dt = db.exec('''
        Select id_intent, name_intent from Intent
    ''')
    if dt.err:
        return [], []
    if len(dt.table) > 0:
        for row in dt.table:
            examples = db.exec('''
                Select text_example from Example where id_intent = {0}
            '''.format(row['id_intent']))
            for example in examples.table:
                x_temp.append(example['text_example'])
                y_temp.append(row['id_intent'])
        return x_temp, y_temp
    else:
        return [], []

vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2,4))

def learn():
    xx, y = fill_intent()
    x = vectorizer.fit_transform(xx)
    return LinearSVC().fit(x, y)

dialog = fill_dialog()
clf = learn()

def get_answer_intent(text):
    db = DB()
    tt = filter_text(text)
    # -----------------------------------------
    # Получение ответа из таблицы классификации
    # -----------------------------------------
    text_vector = vectorizer.transform([text])
    id_intent = clf.predict(text_vector)[0]
    examples = db.exec('''
        Select text_example from Example where id_intent = {0}
    '''.format(id_intent))
    intent = -1
    for example in examples:
       dist = nltk.edit_distance(tt, filter_text(example))
       dist_percentage = dist / len(example)
       if dist_percentage <= setting['PROBA']:
           intent = id_intent
    
    if intent > -1:
        dt = db.exec('''
            Select text_answer from Answer where id_intent = {0}
        '''.format(intent))
        answers = []
        for row in dt.table:
            answers.append(row['text_answer'])

        if len(answers) > 0:
            return random.choice(answers)

    return

def get_answer_failure():
    # -----------------------------------------
    # Получение ответа из таблицы заглушек
    # -----------------------------------------
    db = DB()
  
    dt = db.exec('''
        Select text from Failure where type = 'нет ответа';
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
        return answer, True

    answer = get_answer_template(text)
    if answer:
        return answer, True

    answer = get_answer_dialog(text)
    if answer:
        return answer, True

    answer = get_answer_failure()
    if answer:
        return answer, False
    
    return None, False

class Handler:

    async def post(self, request):
        jsn = await request.json()
        method = jsn['method']
        if method == "learn":
            try:
                result, error = await do(learn, jsn)
                return web.json_response({"result":result,"err":error})
            except Exception as ee:
                return web.json_response({"result":False,"err":str(ee)})


        return web.json_response({"result": False, "err": "Метод не найден", "data": None})

nlp = Handler()