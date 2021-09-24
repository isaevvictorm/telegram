from aiohttp import web
from handlers import *

routes=[
    web.get('/', index.get),
    
    web.get('/login',login.get),
    web.post('/login',login.post),
    web.get('/logout',logout.get),

    web.post('/{token}/', telegram.post),
]
