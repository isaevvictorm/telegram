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

def get_contacts(jsn, user_id = None):
    where = "user_id='{0}'".format(user_id) if user_id else '1=1'
    db = DB()
    dt = db.exec('''
        SELECT
            user_id,
            first_name,
            last_name,
            patronymic,
            birthday,
            username,
            phone_number,
            city,
            email,
            skype,
            date_insert
        FROM Contact WHERE ({0});
    '''.format(where))
    table = []
    for row in dt.table:
        table_row = {
            "user_id": row['user_id'],
            "first_name": row['first_name'],
            "last_name": row['last_name'],
            "patronymic": row['patronymic'],
            "birthday": row['birthday'],
            "username": row['username'],
            "phone_number": row['phone_number'],
            "city": row['city'],
            "email": row['email'],
            "skype": row['skype'],
            "date_insert": str(row['date_insert']),
        }
        table.append(table_row)
    return table

def delete(jsn):
    user_id = jsn['user_id']
    try:
        db = DB()
        dt = db.exec("""
            DELETE FROM Contact where user_id = '{0}';
        """.format(user_id))
        if dt.err:
            return False, str(dt.err)
    except Exception as ee:
        return False, str(ee)
    return True, None

class Handler:
    @template("contacts/index.html")
    async def get(self, request):
        a = Auth(request)
        if await a.is_logged():
            await a.init()
            return {'data':{'first_name':str(a.user.first_name), 'last_name':str(a.user.last_name), 'login': a.user.login, 'admin': a.user.admin, 'breadcrumb':[{'name':'Контакты', 'link':'/contacts'}]}}
        else:
            return web.HTTPFound('/login?redirect=contacts')

    async def post(self, request):
        jsn = await request.json()
        method = jsn['method']
        if method == "get_contacts":
            try:
                table = await do(get_contacts, jsn)
                if len(table) > 0:
                    return web.json_response({'result':True, 'err': None, 'table':table})
                else:
                    return web.json_response({'result':True, 'err': None, 'table':[]})
            except Exception as ee:
                return web.json_response({"result":False,"err":str(ee),"table":[]})
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

contacts = Handler()
