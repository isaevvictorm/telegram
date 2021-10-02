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
    token = dt[0][0] if dt and len(dt) > 0 else None
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
        bot.send_message(message.chat.id, str(message))
    except Exception as ee:
        print(str(ee))

@bot.message_handler(content_types=["photo"])
def text_command(message):
    try:
        bot.send_message(message.chat.id, str(message))
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
