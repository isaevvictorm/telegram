# -*- coding: utf-8 -*-
from aiohttp import web
import asyncio
import telebot
import json
import os
from .modules import DB, setting, generate_answer
from telebot import types

# -============================
# - Токен
# -============================

bot = telebot.TeleBot(setting['TOKEN'])
try:
    bot.remove_webhook()
    bot.set_webhook(url='https://{0}/{1}/'.format(setting['DOMAIN'], setting['TOKEN']))
except Exception as ee:
    print(ee)

@bot.message_handler(commands=['start', 'help'])
def start_command(message):
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
                '{3}' username;
        '''.format( message.from_user.id,
                    message.from_user.first_name,
                    message.from_user.last_name,
                    message.from_user.username))
        if dt.err:
            bot.send_message(message.chat.id, str(dt.err))
        bot.send_message(message.chat.id, str('Привет! Меня зовут Харпер, могу я чем-то помочь?'))
    except Exception as ee:
        print(str(ee))

@bot.message_handler(content_types=["text"])
def text_command(message):
    try:
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
        bot.send_message(message.chat.id, generate_answer(message.text))
    except Exception as ee:
        print(str(ee))

@bot.message_handler(content_types=["photo"])
def text_command(message):
    try:
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
        
        bot.send_message(message.chat.id,  generate_answer(message.text))
    
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
