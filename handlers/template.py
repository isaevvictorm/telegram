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

def get_data(jsn):
    db = DB()
    dt = db.exec('''
        SELECT
            id_template,
            question,
            response,
            date_insert
        FROM 
            Template;
    ''')
    table = []
    for row in dt.table:
        table_row = {
            "id_template": row['id_template'],
            "question": row['question'],
            "response": row['response'],
            "date_insert": row['date_insert']
        }
        table.append(table_row)
    return table

def add(jsn):
    try:
        db = DB()
        dt = db.exec('''
            INSERT INTO Template (question, response)
            SELECT 
                '{0}' as question,
                '{1}' as response
            where 
                '{0}' not in (Select question from Template where question = '{0}' and response = '{1}');
        '''.format(jsn['question'], jsn['response']))
        if dt.err:
            return False, str(dt.err), []

        dt = db.exec('''
            SELECT
                id_template,
                question,
                response,
                date_insert
            FROM 
                Template
            WHERE 
                question = '{0}' and response = '{1}';
        '''.format(jsn['question'], jsn['response']))
        table = [{
            "id_template": dt.table[0]['id_template'],
            "question": dt.table[0]['question'],
            "response": dt.table[0]['response'],
            "date_insert": dt.table[0]['date_insert']
        }]
    except Exception as ee:
        return False, str(ee), []
    return True, None, table


def edit(jsn):
    try:
        db = DB()
        dt = db.exec('''
            Update Template 
            set 
                question = '{0}',
                response = '{1}'
            where 
                id_template = {2};
        '''.format(jsn['question'], jsn['response'], jsn['id_template']))
        if dt.err:
            return False, str(dt.err)
    except Exception as ee:
        return False, str(ee)
    return True, None

def delete(jsn):
    try:
        db = DB()
        dt = db.exec("""
            DELETE FROM Template where id_template = {0};
        """.format(jsn['id_template']))
        if dt.err:
            return False, str(dt.err)
    except Exception as ee:
        return False, str(ee)
    return True, None

class Handler:
    @template("template/index.html")
    async def get(self, request):
        a = Auth(request)
        if await a.is_logged():
            await a.init()
            return {'data':{'first_name':str(a.user.first_name), 'last_name':str(a.user.last_name), 'login': a.user.login, 'id_role': a.user.id_role, 'breadcrumb':[{'name':'Шаблоны', 'link':'/template'}]}}
        else:
            return web.HTTPFound('/login?redirect=template')

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
                table, err, table = await do(add, jsn)
                if err:
                    return web.json_response({'result':False, 'err': str(err), 'table': []})             
                else:
                    return web.json_response({'result':True, 'err': None, 'table': table})
            except Exception as ee:
                return web.json_response({"result":False,"err":str(ee), 'table': []})
        if method == "delete":
            try:
                result, err = await do(delete, jsn)
                if result:
                    return web.json_response({"result":True, "err": None})
                else:
                    return web.json_response({"result":False,"err": str(err)})
            except Exception as ee:
                return web.json_response({"result":False,"err":str(ee)})
        if method == "edit":
            try:
                result, err = await do(edit, jsn)
                if result:
                    return web.json_response({"result":True, "err": None})
                else:
                    return web.json_response({"result":False,"err": str(err)})
            except Exception as ee:
                return web.json_response({"result":False,"err":str(ee)})


        return web.json_response({"result": False, "err": "Метод не найден", "data": None})

template = Handler()