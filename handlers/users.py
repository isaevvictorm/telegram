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

def get_users(jsn, login = None):
    where = "login='{0}'".format(login) if login else '1=1'
    records = db.execute('''
        SELECT
            login,
            first_name,
            last_name,
            admin,
            date_insert
        FROM User WHERE ({0});
    '''.format(where))
    table = []
    for row in records:
        table_row = {
            "login": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "admin": row[3],
            "date_insert": row[4],
        }
        table.append(table_row)
    return table

def add(jsn):
    result = db.executescript('''
        INSERT INTO User (login, first_name, last_name, password, admin)
        SELECT
            '{0}' login,
            '{1}' first_name,
            '{2}' last_name,
            '{3}' password,
            {4} admin;
    '''.format(jsn['data']['login'], jsn['data']['first_name'], jsn['data']['last_name'], sha256(str(jsn['data']['password']).encode('utf-8')).hexdigest(), jsn['data']['admin']))
    # ==========================
    # Предусмотреть вывод ошибок
    # ==========================>>>
    if str(result).lower().find("unique") > -1:
        return [], "Пользователь с таким логином уже существует."
    # ==========================<<<
    table = get_users(jsn, jsn['data']['login'])
    return table, None

def delete(jsn):
    user_id = jsn['login']
    try:
        records = db.execute("""
            DELETE FROM User where login = {0};
        """.format(user_id))
    except Exception as ee:
        return False, str(ee)
    return True, None

class Handler:
    @template("users/index.html")
    async def get(self, request):
        a = Auth(request)
        if await a.is_logged():
            await a.init()
            return {'data':{'first_name':str(a.user.first_name), 'last_name':str(a.user.last_name), 'login': a.user.login, 'admin': a.user.admin, 'breadcrumb':[{'name':'Пользователи', 'link':'/users'}]}}
        else:
            return web.HTTPFound('/login?redirect=users')

    async def post(self, request):
        jsn = await request.json()
        method = jsn['method']
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

users = Handler()
