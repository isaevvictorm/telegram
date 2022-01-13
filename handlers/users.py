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

def get_users(jsn, login = None):
    where = "login='{0}'".format(login) if login else '1=1'
    db = DB()
    dt = db.exec('''
        SELECT
            t1.login,
            t1.first_name,
            t1.last_name,
            t1.id_role,
            t2.name_role,
            t1.date_insert
        FROM 
                User t1
            inner join 
                Role t2 on t1.id_role = t2.id_role
        WHERE ({0});
    '''.format(where))
    table = []
    for row in dt.table:
        table_row = {
            "login": row['login'],
            "first_name": row['first_name'],
            "last_name": row['last_name'],
            "id_role": row['id_role'],
            "name_role": row['name_role'],
            "date_insert": row['date_insert'],
        }
        table.append(table_row)
    return table

def add(jsn):
    db = DB()
    dt = db.exec('''
        INSERT INTO User (login, first_name, last_name, password, id_role)
        SELECT
            '{0}' login,
            '{1}' first_name,
            '{2}' last_name,
            '{3}' password,
            {4} id_role;
    '''.format(jsn['data']['login'], jsn['data']['first_name'], jsn['data']['last_name'], sha256(str(jsn['data']['password']).encode('utf-8')).hexdigest(), jsn['data']['id_role']))
    # ==========================
    # Предусмотреть вывод ошибок
    # ==========================>>>
    if str(dt.err).lower().find("unique") > -1:
        return [], "Пользователь с таким логином уже существует."
    elif dt.err:
        return [], str(dt.err)
    # ==========================<<<
    table = get_users(jsn, jsn['data']['login'])
    return table, None

def delete(jsn):
    user_id = jsn['login']
    try:
        db = DB()
        dt = db.exec("""
            Update User set date_remove = current_timestamp where login = '{0}';
        """.format(user_id))
        if dt.err:
            return False, str(dt.err)
    except Exception as ee:
        return False, str(ee)
    return True, None

class Handler:
    @template("users/index.html")
    async def get(self, request):
        a = Auth(request)
        if await a.is_logged():
            await a.init()
            return {'data':{'first_name':str(a.user.first_name), 'last_name':str(a.user.last_name), 'login': a.user.login, 'id_role': a.user.id_role, 'breadcrumb':[{'name':'Пользователи', 'link':'/users'}]}}
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
                result, err = await do(delete, jsn)
                if result:
                    return web.json_response({"result":True, "err": None})
                else:
                    return web.json_response({"result":False,"err": str(err)})
            except Exception as ee:
                return web.json_response({"result":False,"err":str(ee)})

        return web.json_response({"result": False, "err": "Метод не найден", "data": None})

users = Handler()