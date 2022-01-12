# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from aiohttp import web
from aiohttp_jinja2 import template
import asyncio
from .modules import Auth
from .modules import DB
from .modules import Setting
import telebot

params = Setting()
setting = params.get()

async def do(func, arg_obj):
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers = 100)
    return await loop.run_in_executor(executor, func, arg_obj)

def send_message(jsn):
    try:
        setting = params.get()
        db = DB()
        last = db.exec('''
            Select max(rid) as rid from Message;
        ''')
        dt = db.exec('''
            INSERT INTO Message  (chat__id, text, from_me, answer_for, from_user__id)
            SELECT
                '{0}' as chat_id,
                '{1}' as text,
                {2} as from_me,
                '{3}' as answer_for,
                '{0}' as from_user__id;       
            '''.format(jsn['chat__id'] if 'chat__id' in jsn else '', jsn['text'] if 'text' in jsn else '', jsn['from_me'] if 'from_me' in jsn else '', jsn['answer_for'] if 'answer_for' in jsn else ''))

        db.exec('''
            INSERT INTO Template  (question, response)
            SELECT
                '{0}' as question,
                '{1}' as response
            WHERE 
                '{0}' not in (Select question from Template where question = '{0}' and response = '{1}')
            '''.format(jsn['answer_for'] if 'answer_for' in jsn else '', jsn['text'] if 'text' in jsn else ''))
        
        bot = telebot.TeleBot(setting['TOKEN'])
        bot.send_message(jsn['chat__id'] if 'chat__id' in jsn else '', jsn['text'] if 'text' in jsn else 'Спасибо за Ваше сообщение, мы скоро на него ответим...')
        try:
            rid = int(last.table[0]['rid']) + 1
        except:
            rid = -1
        return True, rid
    except Exception as ee:
        return False, str(ee)

def get_contacts(jsn):
    try:
        db = DB()
        dt = db.exec('''
            Select
                t1.first_name,
                t1.last_name,
                t2.text as message,
                t2.date_insert,
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
                        max(t2.rid) as rid
                    FROM
                        Contact t1
                        inner join
                        Message t2 on t1.user_id = t2.from_user__id
                    WHERE
                        date_answer is null and t1.online = 1
                    GROUP BY
                        first_name,
                        last_name,
                        username,
                        t1.user_id
                )t1
            inner join
                Message t2 on t1.user_id = t2.from_user__id and t1.rid = t2.rid
            order by 
                t2.rid desc;
        ''')
        if dt.err:
            return False, str(dt.err), []
        
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
        return True, table, None
    except Exception as ee:
        return False, str(ee), []

def get_message(jsn):
    setting = params.get()
    try:
        db = DB()
        where = "and rid > {0}".format(jsn['rid']) if 'rid' in jsn else ""
        dt = db.exec('''
            Select
                rid,
                message as message,
                from_me,
                date_insert
            from
                (
                    SELECT
                        rid,
                        text as message,
                        from_me,
                        date_insert
                    from
                        Message
                    WHERE
                        from_user__id = '{0}' {2}
                    order by
                        date_insert desc
                    limit {1}
                )tt
            order by
                date_insert asc;
        '''.format(jsn['chat__id'], setting['CNT_MESSAGE_IN_CHAT'], where))
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

def close(jsn):
    try:
        db = DB()
        dt = db.exec('''
           Update Contact set online = 0
           WHERE user_id = {0};
        '''.format(jsn['user_id']))
        if dt.err:
            return False, str(dt.err)
        return True, None
    except Exception as ee:
        return False, str(ee)

class Handler:
    @template("chats/index.html")
    async def get(self, request):
        a = Auth(request)
        if await a.is_logged():
            await a.init()
            return {'data':{'first_name':str(a.user.first_name), 'last_name':str(a.user.last_name), 'login': a.user.login, 'id_role': a.user.id_role, 'breadcrumb':[{'name':'Чаты', 'link':'/chats'}]}}
        else:
            return web.HTTPFound('/login?redirect=chats')

    async def post(self, request):
        jsn = await request.json()
        method = jsn['method']
        if method == "send_message":
            try:
                result, err = await do(send_message, jsn)
                if result:
                    return web.json_response({'result':True, 'err': err})
                else:
                    return web.json_response({'result':False, 'err': str(err)})
            except Exception as ee:
                return web.json_response({"result":False,"err":str(ee)})
        if method == "get_contacts":
            try:
                result, table, error = await do(get_contacts, jsn)
                if result:
                    return web.json_response({'result':True, 'err': None, 'table':table})
                else:
                    return web.json_response({'result':True, 'err': error, 'table':[]})
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
        if method == "close":
            try:
                result, error = await do(close, jsn)
                return web.json_response({"result":result,"err":error})
            except Exception as ee:
                return web.json_response({"result":False,"err":str(ee)})


        return web.json_response({"result": False, "err": "Метод не найден", "data": None})

chats = Handler()
