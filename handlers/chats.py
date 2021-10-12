# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from aiohttp import web
from aiohttp_jinja2 import template
import asyncio
from .modules import Auth
from .modules import db

async def do(func, arg_obj):
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers = 100)
    return await loop.run_in_executor(executor, func, arg_obj)

def send_message(jsn):
    dt = db.execute('''
    INSERT INTO Message  (chat_id, text, from_me)
    SELECT
        '{0}' as chat_id,
        '{1}' as text,
        1 as from_me;
    '''.format(jsn['chat_id'], jsn['text'], jsn['from_me']))
    return True

def get_contacts(jsn):
    records = db.execute('''
        Select
            t1.first_name,
            t1.last_name,
            t1.username,
            t2.text as message,
            t1.date_insert
        from
        (
            SELECT
                t1.user_id,
                first_name,
                username,
                last_name,
                max(t2.date_insert) as date_insert
            FROM
                Contact t1
                inner join
                Message t2 on t1.user_id = t2.chat__id
            WHERE
                date_answer is null
            GROUP BY
                first_name,
                last_name,
                username,
                t1.user_id
        )t1
        inner join
        Message t2 on t1.user_id = t2.chat__id and t1.date_insert = t2.date_insert
        order by t2.date_insert desc
        ;
    ''')
    table = []
    for row in records:
        table_row = {
            "first_name": row[0],
            "last_name": row[1],
            "message": row[2],
            "date_insert": str(row[3]),
        }
        table.append(table_row)
    return table

def get_message(jsn):
    try:
        dt = db.execute('''
            SELECT
                *
            from
                Message;
        ''')
        return dt, None
    except Exception as ee:
        return None, str(ee)

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
        if method == "get_contacts":
            try:
                table = await do(get_contacts, jsn)
                if len(table) > 0:
                    return web.json_response({'result':True, 'err': None, 'table':table})
                else:
                    return web.json_response({'result':True, 'err': None, 'table':[]})
            except Exception as ee:
                return web.json_response({"result":False,"err":str(ee),"table":[]})
        if method == "get_message":
            try:
                table, err = await do(get_message, jsn)
                if err:
                    return web.json_response({'result':False, 'err': str(err), 'table':[]})
                else:
                    return web.json_response({'result':True, 'err': None, 'table':table})
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
