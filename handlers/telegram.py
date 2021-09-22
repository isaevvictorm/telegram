# -*- coding: utf-8 -*-
from aiohttp import web
import asyncio
import telebot
import json
from .modules import db
from telebot import types

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
