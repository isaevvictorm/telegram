# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from aiohttp import web
from aiohttp_jinja2 import template
import asyncio
from .modules import Auth
from .modules import DB
from hashlib import sha256

async def do(func, arg_obj):
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=100)
    return await loop.run_in_executor(executor, func, arg_obj)

def get_data(jsn, login = None):
    db = DB()
    dt = db.exec('''
        SELECT
            rid,
            text,
            date_insert
        FROM 
            Plug
        WHERE type = '{0}';
    '''.format(jsn['type']))
    table = []
    for row in dt.table:
        table_row = {
            "rid": row['rid'],
            "text": row['text'],
            "date_insert": row['date_insert']
        }
        table.append(table_row)
    return table


def add(jsn):
    try:
        db = DB()
        dt = db.exec('''
            INSERT INTO Plug (text, type)
            SELECT '{0}' as text, '{1}' as type
            WHERE 
                '{0}' not in (Select text from Plug where text = '{0}' and type = '{1}');
        '''.format(jsn['data']['text'], jsn['data']['type']))

        if dt.err:
            return False, str(dt.err), []

        dt = db.exec('''
            SELECT
                rid,
                text,
                date_insert
            FROM 
                Plug
            WHERE 
                text = '{0}' and type = '{1}';
        '''.format(jsn['data']['text'], jsn['data']['type']))

        table = [{
            "rid": dt.table[0]['rid'],
            "text": dt.table[0]['text'],
            "date_insert": dt.table[0]['date_insert']
        }]

    except Exception as ee:
        return False, str(ee), []

    return True, None, table


def delete(jsn):
    try:
        db = DB()
        dt = db.exec("""
            DELETE FROM Plug where rid = {0};
        """.format(jsn['rid']))
        if dt.err:
            return False, str(dt.err)
    except Exception as ee:
        return False, str(ee)
    return True, None

class Handler:
    @template("plug/index.html")
    async def get(self, request):
        a = Auth(request)
        if await a.is_logged():
            await a.init()
            return {'data':{'first_name':str(a.user.first_name), 'last_name':str(a.user.last_name), 'login': a.user.login, 'id_role': a.user.id_role, 'breadcrumb':[{'name':'Пользователи', 'link':'/plug'}]}}
        else:
            return web.HTTPFound('/login?redirect=plug')

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
                result, err, table = await do(add, jsn)
                if result:
                    return web.json_response({'result': True, 'err': None, 'table': table })             
                else:
                    return web.json_response({'result':False, 'err': str(err), 'table': []})
            except Exception as ee:
                return web.json_response({"result":False, "err":str(ee),'table': [] })
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

plug = Handler()