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
    token = dt[0][0] if len(dt) > 0 else None
    if token:
        bot = telebot.TeleBot(token)
        bot.remove_webhook()
        if os.path.exists(os.path.join(os.getcwd() + "/", setting['WEBHOOK_SSL_CERT'])):
            bot.set_webhook(url='https://{0}:{1}/{2}/'.format(setting['SERVER_IP'], setting['WEBHOOK_PORT'], get_token()), certificate=open(os.path.join(os.getcwd() + "/", setting['WEBHOOK_SSL_CERT']), 'r'))
        else:
            print('Error webhook: SERT not found')
    return token[0][0] if len(token) > 0 else None

token = get_token()
bot = telebot.TeleBot(token)

@bot.message_handler(content_types=["text"])
def text_command(message):
    try:
        bot.send_message(message.chat.id, str(message))
    except Exception as ee:
        print(str(ee))

class Handler:
    async def get(self, request):
        return web.json_response({"result":"success"})

    async def post(self, request):
        if request.match_info.get("token") == TOKEN:
            request_body_jsn = await request.json()
            update = telebot.types.Update.de_json(request_body_jsn)
            bot.process_new_updates([update])
            return web.Response()
        else:
            return web.Response(status = 403)

telegram = Handler()
