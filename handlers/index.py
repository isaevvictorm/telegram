# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from aiohttp import web
from aiohttp_jinja2 import template
import asyncio
from .modules import Auth

class Handler:
    @template("index.html")
    async def get(self, request):
        a = Auth(request)
        if await a.is_logged():
            await a.init()
            return {'data':{'first_name':str(a.user.first_name), 'last_name':str(a.user.last_name), 'login': a.user.login, 'id_role': a.user.id_role}}
        else:
            return web.HTTPFound('/login')

index = Handler()
