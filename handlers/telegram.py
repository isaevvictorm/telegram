# -*- coding: utf-8 -*-
from aiohttp import web
import asyncio
import telebot
import json
import os
from .modules import db, setting
from telebot import types

def get_token():
    dt = db.execute('''
        SELECT token FROM Webhook WHERE status = 1;
    ''', True)
    token = dt[0][0] if dt and len(dt) > 0 else setting['TOKEN_DEBUG']
    if token:
        bot = telebot.TeleBot(token)
        bot.remove_webhook()
        if os.path.exists(os.path.join(os.getcwd() + "/", setting['WEBHOOK_SSL_CERT'])):
            bot.set_webhook(url='https://{0}:{1}/{2}/'.format(setting['DOMEN'] if len(setting['DOMEN']) > 0 else setting['SERVER_IP'], setting['WEBHOOK_PORT'], token), certificate=open(os.path.join(os.getcwd() + "/", setting['WEBHOOK_SSL_CERT']), 'r'))
        else:
            print('Error webhook: SERT not found')
    return token

bot = telebot.TeleBot(get_token())

@bot.message_handler(content_types=["text"])
def text_command(message):
    try:
        dt = db.executescript('''
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
        bot.send_message(message.chat.id, str('Спасибо за Ваше сообщение, мы скоро на него ответим...'))
    except Exception as ee:
        print(str(ee))

@bot.message_handler(content_types=["photo"])
def text_command(message):
    try:
        dt = db.executescript('''
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
        bot.send_message(message.chat.id, str('Спасибо за Ваше сообщение, мы скоро на него ответим...'))
    except Exception as ee:
        print(str(ee))

class Handler:
    async def get(self, request):
        return web.json_response({"result":"success"})

    async def post(self, request):
        #request.match_info.get("token")
        request_body_jsn = await request.json()
        update = telebot.types.Update.de_json(request_body_jsn)
        bot.process_new_updates([update])
        return web.Response()

telegram = Handler()
