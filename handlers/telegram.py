# -*- coding: utf-8 -*-
from aiohttp import web
import asyncio
import telebot
import json
from .modules import DB, Setting
from telebot import types
import random 
from .nlp import generate_answer

# -============================
# - Токен
# -============================

params = Setting()
setting = params.get()

bot = telebot.TeleBot(setting['TOKEN'])
try:
    bot.remove_webhook()
    bot.set_webhook(url='https://{0}/{1}/'.format(setting['DOMAIN'], setting['TOKEN']))
except Exception as ee:
    print(ee)

def get_fast_answer(type):
    # -----------------------------------------
    # Получение ответа из таблицы заглушек
    # -----------------------------------------
    db = DB()
  
    dt = db.exec('''
        Select text from Plug where type = '{0}';
    '''.format(type))
    
    dictionary = []

    for row in dt.table:
        dictionary.append(row['text'])

    if len(dictionary) == 0:
        return
    else:
        return random.sample(dictionary, 1)[0]


def save_answer(jsn):
    try:
        db = DB()
        dt = db.exec('''
            INSERT INTO Message  (chat__id, text, from_me, from_user__id)
            SELECT
                '{0}' as chat_id,
                '{1}' as text,
                {2} as from_me,
                '{3}' as from_user__id;
            '''.format(jsn['chat__id'] if 'chat__id' in jsn else '', jsn['text'] if 'text' in jsn else '', jsn['from_me'] if 'from_me' in jsn else '', jsn['from_user__id'] if 'from_user__id' in jsn else ''))
        return True, None
    except Exception as ee:
        return False, str(ee)


def save_user(message):
    try:
        db = DB()
        dt = db.exec('''
            INSERT INTO Contact (
                user_id,
                first_name,
                last_name,
                username
            )
            Select
                '{0}' user_id,
                '{1}' first_name,
                '{2}' last_name,
                '{3}' username
            WHERE
                '{0}' not in (Select user_id from Contact where user_id = '{0}')
        '''.format( message.from_user.id,
                    message.from_user.first_name,
                    message.from_user.last_name,
                    message.from_user.username))
        if dt.err:
            bot.send_message(setting['ADMIN'], str(dt.err))
    except Exception as ee:
        bot.send_message(setting['ADMIN'], str(ee))


@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        save_user(message)
        answer =  get_fast_answer('Приветствие')
        if answer:
            bot.send_message(message.chat.id, answer)
    except Exception as ee:
        bot.send_message(setting['ADMIN'], str(ee))

@bot.message_handler(commands=['help'])
def start_command(message):
    try:
        save_user(message)
        db = DB()
        db.exec('''
            Update Contact set online = 1
            WHERE user_id = {0};
        '''.format(message.from_user.id))
        bot.send_message(message.chat.id, 'Специалист свяжется с Вами в ближайшее время. Ожидайте.')
    except Exception as ee:
        bot.send_message(setting['ADMIN'], str(ee))

@bot.message_handler(content_types=['contact'])
def start_command(message):
    try:
        db = DB()
        dt = db.exec('''
            Update Contact set phone_number = '{1}'
            WHERE 
                user_id = {0};
        '''.format( message.from_user.id,
                    message.contact.phone_number))
        if dt.err:
            bot.send_message(setting['ADMIN'], str(dt.err))
        answer =  get_fast_answer('Контакт')
        if answer:
            bot.send_message(message.chat.id, answer)
    except Exception as ee:
        bot.send_message(setting['ADMIN'], str(dt.err))


@bot.message_handler(content_types=["text"])
def text_command(message):
    try:
        save_user(message)

        db = DB()
        dt = db.exec('''
            INSERT INTO Message (
                content_type,
                message_id,
                from_user__id,
                is_bot,
                chat__id,
                text,
                from_me,
                date
            )
            Select
                'text' as content_type,
                {0} as message_id,
                '{1}' as from_user__id,
                0 as is_bot,
                '{2}' as chat__id,
                '{3}' as text,
                0 as from_me,
                {4} as date;
        '''.format(message.message_id, message.from_user.id, message.chat.id, message.text, message.date))
        if dt.err:
            bot.send_message(message.chat.id, str(dt.err))
        answer, result = generate_answer(message.text)
        if result == False:
            db.exec('''
                Update Contact set online = 1
                WHERE user_id = {0};
            '''.format(message.from_user.id))
        if (answer and result == True) or (answer and message.chat.id == message.from_user.id):
            bot.send_message(message.chat.id,  answer)
            jsn = {
                "chat__id": message.chat.id,
                "from_me": 1,
                "text": answer,
                "from_user__id": message.from_user.id
            }
            save_answer(jsn)
    except Exception as ee:
        print(str(ee))

@bot.message_handler(content_types=["photo"])
def text_command(message):
    try:
        save_user(message)

        db = DB()
        dt = db.exec('''
            INSERT INTO Message (
                content_type,
                message_id,
                from_user__id,
                is_bot,
                chat__id,
                caption,
                from_me,
                date,
                file_id,
                file_unique_id
            )
            Select
                'photo' as content_type,
                {0} as message_id,
                '{1}' as from_user__id,
                0 as is_bot,
                '{2}' as chat__id,
                '{3}' as caption,
                0 as from_me,
                {4} as date,
                '{5}' as file_id,
                '{6}' as file_unique_id;
        '''.format(message.message_id, message.from_user.id, message.chat.id, message.text, message.date, json.dumps(message.json)['photo'][2]['file_id'], json.dumps(message.json)['photo'][2]['file_unique_id']))
        if dt.err:
            bot.send_message(message.chat.id, str(dt.err))
        
        answer, result = generate_answer(message.text)
        if result == False:
            db.exec('''
                Update Contact set online = 1
                WHERE user_id = {0};
            '''.format(message.from_user.id))
        if (answer and result == True) or (answer and message.chat.id == message.from_user.id):
            bot.send_message(message.chat.id,  answer)
            jsn = {
                "chat__id": message.chat.id,
                "from_me": 1,
                "text": answer,
                "from_user__id": message.from_user.id
            }
            save_answer(jsn)
    except Exception as ee:
        print(str(ee))

class Handler:
    async def get(self, request):
        return web.json_response({"result":"success"})

    async def post(self, request):
        request_body_jsn = await request.json()
        update = telebot.types.Update.de_json(request_body_jsn)
        bot.process_new_updates([update])
        return web.Response()

telegram = Handler()
