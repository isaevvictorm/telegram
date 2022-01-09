# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from aiohttp import web
from aiohttp_jinja2 import template
import asyncio
from .modules import Auth
from .modules import DB
from .modules import setting
import telebot

async def do(func, arg_obj):
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers = 100)
    return await loop.run_in_executor(executor, func, arg_obj)

def send_message(jsn):
    try:
        db = DB()
        dt = db.exec('''
            INSERT INTO Message  (chat__id, text, from_me, answer_for)
            SELECT
                '{0}' as chat_id,
                '{1}' as text,
                {2} as from_me,
                '{3}' as answer_for;
            '''.format(jsn['chat__id'] if 'chat__id' in jsn else '', jsn['text'] if 'text' in jsn else '', jsn['from_me'] if 'from_me' in jsn else '', jsn['answer_for'] if 'answer_for' in jsn else ''))
        bot = telebot.TeleBot(setting['TOKEN'])
        bot.send_message(jsn['chat__id'] if 'chat__id' in jsn else '', jsn['text'] if 'text' in jsn else 'Спасибо за Ваше сообщение, мы скоро на него ответим...')
        return True, None
    except Exception as ee:
        return False, str(ee)

def get_contacts(jsn):
    db = DB()
    dt = db.exec('''
        Select
            t1.first_name,
            t1.last_name,
            t2.text as message,
            t1.date_insert,
            t1.username,
            t1.user_id,
            t2.from_me
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
        order by 
            t2.date_insert desc
        ;
    ''')
    table = []
    for row in dt.table:
        table_row = {
            "first_name": row['first_name'],
            "last_name": row['last_name'],
            "message": row['message'],
            "date_insert": str(row['date_insert']),
            "username": str(row['username']),
            "user_id": str(row['user_id']),
            "from_me": row['from_me'],
        }
        table.append(table_row)
    return table

def get_message(jsn):
    try:
        db = DB()
        dt = db.exec('''
            SELECT
                rid,
                text as message,
                from_me,
                date_insert
            from
                Message
            WHERE
                chat__id = '{0}'
            order by
                date_insert asc;
        '''.format(jsn['chat__id']))
        if dt.err:
            return False, [], str(dt.err)
        table = []
        for row in dt.table:
            table_row = {
                "rid": row['rid'],
                "message": row['message'],
                "from_me": row['from_me'],
                "date_insert": row['date_insert'],
            }
            table.append(table_row)
        return True, table, None
    except Exception as ee:
        return False, [], str(ee)

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
                result, err = await do(send_message, jsn)
                if result:
                    return web.json_response({'result':True, 'err': None})
                else:
                    return web.json_response({'result':False, 'err': str(dt.err)})
            except Exception as ee:
                return web.json_response({"result":False,"err":str(ee)})
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
                result, table, err = await do(get_message, jsn)
                if result:
                    return web.json_response({'result':True, 'err': None, 'table':table})
                else:
                    return web.json_response({'result':False, 'err': str(err), 'table':[]})
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
