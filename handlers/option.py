# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from aiohttp import web
from aiohttp_jinja2 import template
import asyncio
from .modules import Auth
from .modules import DB
from hashlib import sha256
import os
from .modules import Setting

params = Setting()
setting = params.get()

async def do(func, arg_obj):
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=100)
    return await loop.run_in_executor(executor, func, arg_obj)

def get_data(jsn):
    db = DB()
    dt = db.exec('''
        SELECT
            name,
            value || '&&' || type || '&&' || name as value,
            description,
            type,
            date_insert
        FROM
            Setting;
    ''')
    table = []
    for row in dt.table:
        table_row = {
            "name": row['name'],
            "value": str(row['value']),
            "description": row['description'],
            "type": row['type'],
            "date_insert": row['date_insert'],
        }
        table.append(table_row)
    return table

def update(jsn):
    try:
        db = DB()
        dt = db.exec("""
            Update Setting set value = '{1}' where name = '{0}';
        """.format(jsn['param'], jsn['value']))
        if dt.err:
            return False, str(dt.err)
    except Exception as ee:
        return False, str(ee)
    return True, None

def restart(jsn):
    setting = params.get()
    os.system("pm2 restart {0}".format(setting('APP_NAME')))
    return True

class Handler:
    @template("option/index.html")
    async def get(self, request):
        a = Auth(request)
        if await a.is_logged():
            await a.init()
            return {'data':{'first_name':str(a.user.first_name), 'last_name':str(a.user.last_name), 'login': a.user.login, 'id_role': a.user.id_role, 'breadcrumb':[{'name':'Настройки', 'link':'/option'}]}}
        else:
            return web.HTTPFound('/login?redirect=option')

    async def post(self, request):
        jsn = await request.json()
        method = jsn['method']
        if method == "get":
            try:
                table = await do(get_data, jsn)
                if len(table) > 0:
                    return web.json_response({'result':True, 'err': None, 'table':table})
                else:
                    return web.json_response({'result':True, 'err': None, 'table':[]})
            except Exception as ee:
                return web.json_response({"result":False,"err":str(ee),"table":[]})
        if method == "restart":
            try:
                result = await do(restart, jsn)
                if result:
                    return web.json_response({"result":True, "err": None})
                else:
                    return web.json_response({"result":False,"err": None})
            except Exception as ee:
                return web.json_response({"result":False,"err": str(ee)})
        if method == "update":
            try:
                result, err = await do(update, jsn)
                if result:
                    return web.json_response({"result":True, "err": None})
                else:
                    return web.json_response({"result":False,"err": str(err)})
            except Exception as ee:
                return web.json_response({"result":False,"err":str(ee)})

        return web.json_response({"result": False, "err": "Метод не найден", "data": None})

option = Handler()