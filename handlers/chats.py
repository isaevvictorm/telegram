# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from aiohttp import web
from aiohttp_jinja2 import template
import asyncio
from .modules import Auth
from .modules import db

def send_message(jsn):
    dt = db.execute('''
    INSERT INTO Message (chat_id, text, from_me)
    SELECT
        '{0}' as chat_id,
        '{1}' as text,
        1 as from_me
    '''.format(jsn['chat_id'], jsn['text'], jsn['from_me']))
    return True

class Handler:
    @template("chats/index.html")
    async def get(self, request):
        a = Auth(request)
        if await a.is_logged():
            await a.init()
            return {'data':{'first_name':str(a.user.first_name), 'last_name':str(a.user.last_name), 'login': a.user.login, 'admin': a.user.admin, 'breadcrumb':[{'name':'Чаты', 'link':'/chats'}]}}
        else:
            return web.HTTPFound('/login?redirect=chats')

    async def post(self, request):
        jsn = await request.json()
        method = jsn['method']
        if method == "send_message":
            try:
                result = await do(send_message, jsn)
                if result:
                    return web.json_response({'result':True, 'err': None})
                else:
                    return web.json_response({'result':False, 'err': None})
            except Exception as ee:
                return web.json_response({"result":False,"err":str(ee),"table":[]})
        if method == "get_users":
            try:
                table = await do(get_users, jsn)
                if len(table) > 0:
                    return web.json_response({'result':True, 'err': None, 'table':table})
                else:
                    return web.json_response({'result':True, 'err': None, 'table':[]})
            except Exception as ee:
                return web.json_response({"result":False,"err":str(ee),"table":[]})
        if method == "add":
            try:
                table, err = await do(add, jsn)
                if err:
                    return web.json_response({'result':False, 'err': str(err), 'table':[]})
                elif table and len(table) > 0:
                    return web.json_response({'result':True, 'err': None, 'table':table})
                else:
                    return web.json_response({'result':False, 'err': "Не удалось добавить пользователя.", 'table':[]})
            except Exception as ee:
                return web.json_response({"result":False,"err":str(ee),"table":[]})
        if method == "delete":
            try:
                result, error = await do(delete, jsn)
                return web.json_response({"result":result,"err":error})
            except Exception as ee:
                return web.json_response({"result":False,"err":str(ee)})


        return web.json_response({"result": False, "err": "Метод не найден", "data": None})

chats = Handler()
