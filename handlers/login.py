from aiohttp import web
from aiohttp_jinja2 import template
from aiohttp_session import  get_session
from .modules.auth import Auth
import json

class LoginHandler:
    @template('login.html')
    async def get(self,request):
        a = Auth(request)
        if await a.is_logged():
            url = ""
            try:
                params = request.rel_url.query
                url = params['redirect']
            except:
                pass
            return web.HTTPFound('/{0}'.format(str(url)))
        return {}

    @template('index.html')
    async def post(self, request):
        a = Auth(request)
        await a.logout()
        await a.sign()
        await a.init()
        if (a.user and a.user.login):
            return web.Response(text=json.dumps({'result':{'userid':a.user.login, 'last_name':a.user.last_name, 'first_name':a.user.first_name, 'admin': a.user.admin}}),content_type="application/json")
        else:
            return web.Response(text=json.dumps({'result':False}), content_type="application/json")

class LogoutHandler:
    async def get(self,request):
        a = Auth(request)
        await a.logout()
        return web.HTTPFound('/login')

login = LoginHandler()
logout = LogoutHandler()
