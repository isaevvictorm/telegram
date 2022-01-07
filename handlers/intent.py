# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from aiohttp import web
from aiohttp_jinja2 import template
import asyncio
from .modules import Auth
from .modules import DB

async def do(func, arg_obj):
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=100)
    return await loop.run_in_executor(executor, func, arg_obj)

def get_data(jsn, login = None):
    db = DB()
    dt = db.exec('''
        SELECT
            id_intent,
            name_intent,
            date_insert
        FROM Intent;
    ''')
    table = []
    for row in dt.table:
        table_row = {
            "id_intent": row['id_intent'],
            "name_intent": row['name_intent'],
            "date_insert": row['date_insert']
        }
        table.append(table_row)
    return table

def add(jsn):
    try:
        db = DB()
        dt = db.exec('''
            INSERT INTO Intent (name_intent)
            SELECT '{0}' as name_intent
        '''.format(jsn['data']['name_intent']))
        if dt.err:
            return False. str(dt.err)
    except Exception as ee:
        return False, str(ee)
    return True, None

def delete(jsn):
    try:
        db = DB()
        dt = db.exec("""
            DELETE FROM Intent where id_intent = {0};
        """.format(jsn['id_intent']))
        if dt.err:
            return False, str(dt.err)
    except Exception as ee:
        return False, str(ee)
    return True, None

class Handler:
    @template("intent/index.html")
    async def get(self, request):
        a = Auth(request)
        if await a.is_logged():
            await a.init()
            return {'data':{'first_name':str(a.user.first_name), 'last_name':str(a.user.last_name), 'login': a.user.login, 'admin': a.user.admin, 'breadcrumb':[{'name':'Знания', 'link':'/intent'}]}}
        else:
            return web.HTTPFound('/login?redirect=intent')

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
        if method == "add":
            try:
                table, err = await do(add, jsn)
                if err:
                    return web.json_response({'result':False, 'err': str(err)})             
                else:
                    return web.json_response({'result':True, 'err': None})
            except Exception as ee:
                return web.json_response({"result":False,"err":str(ee)})
        if method == "delete":
            try:
                result, err = await do(delete, jsn)
                if result:
                    return web.json_response({"result":True, "err": None})
                else:
                    return web.json_response({"result":False,"err": str(err)})
            except Exception as ee:
                return web.json_response({"result":False,"err":str(ee)})


        return web.json_response({"result": False, "err": "Метод не найден", "data": None})

intent = Handler()