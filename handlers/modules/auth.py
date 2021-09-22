
from aiohttp_session import get_session
from hashlib import sha256
import db

class User:
    login = None
    first_name = None
    last_name = None
    #=============
    #= Роли
    #=============>>>
    admin = None
    #=============<<<

    async def get(self, login):
        #=============>>>
        # users = Данные из БД
        #=============<<<
        for user in users:
            if str(user['login']).lower() == str(login).lower():
                return User().set_data(login, user['first_name'], user['last_name'], user['admin'])
        raise Exception("Пользователь не найден...")

    def set_data(self, login, first_name, last_name, admin):
        self.login = login
        self.first_name = first_name
        self.last_name = last_name
        self.admin = admin
        return self

class Auth:
    def __init__(self, request):
        self.request = request
        self.login = None
        self.first_name = None
        self.last_name = None
        self.admin = None

    async def init(self):
        session = await get_session(self.request)
        self.login = await self.get_user(session.get('login'))
        self.first_name = await self.get_user(session.get('first_name'))
        self.last_name = await self.get_user(session.get('last_name'))
        self.admin = await self.get_user(session.get('admin'))
        return None

    async def is_logged(self):
        session = await get_session(self.request)
        if session.get('login'):
            return True
        else:
            return False

    async def authenticate(self, login, password):
        #=============>>>
        # users = Данные из БД
        #=============<<<
        for user in users:
            if str(user['login']).lower() == str(login).lower() and str(user['password']).lower() == str(password).lower():
                return User().set_data(str(login), str(user['first_name']), str(user['last_name']), str(user['admin']))
        return None

    async def get_user(self, login):
        #=============>>>
        # users = Данные из БД
        #=============<<<
        for user in users:
            if str(user['login']).lower() == str(login).lower():
                u = type("CpUser",(),user)()
                return u
        return None

    async def logout(self):
        session = await get_session(self.request)
        session['login'] = None
        session['first_name'] = None
        session['last_name'] = None
        session['admin'] = None
        return True

    async def login(self):
        try:
            session = await get_session(self.request)
            if self.request.content_type == "application/json":
                jsn = await self.request.json()
                login = str(jsn['login'])
                password = str(jsn['password'])
                u = await self.authenticate(login, password)
                if u:
                    session['login'] = u.login
                    session['first_name'] = u.first_name
                    session['last_name'] = u.last_name
                    session['admin'] = u.admin
                    return True
                else:
                    return False
            else:
                return False
        except Exception as ee:
            print('ERROR login():', str(ee))
