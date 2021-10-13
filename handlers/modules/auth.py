
from aiohttp_session import get_session
from hashlib import sha256
from .db import DB

class User:
    login = None
    first_name = None
    last_name = None
    #=============
    #= Роли
    #=============>>>
    admin = None
    #=============<<<

    def set(self, login, first_name, last_name, admin):
        self.login = login
        self.first_name = first_name
        self.last_name = last_name
        self.admin = admin
        return self

class Auth:
    def __init__(self, request):
        self.request = request
        self.user = None

    async def init(self):
        session = await get_session(self.request)
        self.user = await self.get_user(session.get('login'))
        return None

    async def is_logged(self):
        session = await get_session(self.request)
        if session.get('login'):
            return True
        else:
            return False

    async def authenticate(self, login, password):
        db = DB(True)
        dt = db.exec('''
            Select login, first_name, last_name, admin, password from User
        ''')
        print(str(dt.table))
        users = []
        for row in dt.table:
            users.append({
                "login":row['login'],
                "first_name":row['first_name'],
                "last_name":row['last_name'],
                "admin":row['admin'],
                "password":row['password']
            })
        for user in users:
            if str(user['login']).lower() == str(login).lower() and str(user['password']).lower() == sha256(password.encode('utf-8')).hexdigest().lower():
                return User().set(str(login), str(user['first_name']), str(user['last_name']), str(user['admin']))
        return None

    async def get_user(self, login):
        db = DB(True)
        dt = db.exec('''
            Select login, first_name, last_name, admin from User WHERE login = '{0}'
        '''.format(login))
        if dt:
            users = []
            for row in dt.table:
                users.append({
                    "login":row['login'],
                    "first_name":row['first_name'],
                    "last_name":row['last_name'],
                    "admin":row['admin']
                })
            for user in users:
                if str(user['login']).lower() == str(login).lower():
                    u = type("CpUser",(),user)()
                    return u
        return None

    async def logout(self):
        session = await get_session(self.request)
        session['login'] = None
        return True

    async def sign(self):
        #try:
        session = await get_session(self.request)
        if self.request.content_type == "application/json":
            jsn = await self.request.json()
            login = str(jsn['login'])
            password = str(jsn['password'])
            u = await self.authenticate(login, password)
            if u:
                session['login'] = u.login
                return True
            else:
                return False
        else:
            return False
        #except Exception as ee:
        #    print('Error:', str(ee))
        #    return False
