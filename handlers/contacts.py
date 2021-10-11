# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from aiohttp import web
from aiohttp_jinja2 import template
import asyncio
from .modules import Auth
from .modules import db
from hashlib import sha256

async def do(func, arg_obj):
    loop = asyncio.get_event_loop()
    executor = ThreadPoolExecutor(max_workers=100)
    return await loop.run_in_executor(executor, func, arg_obj)

def get_contacts(jsn, user_id = None):
    where = "user_id='{0}'".format(user_id) if user_id else '1=1'
    records = db.execute('''
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
    for row in records:
        table_row = {
            "user_id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "patronymic": row[3],
            "birthday": row[4],
            "username": row[5],
            "phone_number": row[6],
            "city": row[7],
            "email": row[8],
            "skype": row[9],
            "date_insert": str(row[10]),
        }
        table.append(table_row)
    return table

def delete(jsn):
    user_id = jsn['user_id']
    try:
        records = db.executescript("""
            DELETE FROM Contact where user_id = '{0}';
        """.format(user_id))
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
