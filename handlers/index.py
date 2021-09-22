# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from aiohttp import web
from aiohttp_jinja2 import template
import asyncio
from .module import Auth

class Handler:
    @template("index.html")
    async def get(self, request):
        a = Auth(request)
        if await a.is_logged():
            await a.init()
            return {'data':{'first_name':str(a.login.first_name), 'last_name':str(a.login.last_name), 'login': a.login.login, 'admin': a.login.admin}}
        else:
            return web.HTTPFound('/login')

index = Handler()
