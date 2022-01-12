from aiohttp import web
from handlers import *

routes=[
    web.get('/', index.get),

    web.get('/login',login.get),
    web.post('/login',login.post),
    web.get('/logout',logout.get),

    web.post('/{token}/', telegram.post),

    # ---------------------------
    # Управление пользователями
    # ---------------------------
    web.post('/users',users.post),
    web.get('/users',users.get),
    # ---------------------------
    # Управление чатами
    # ---------------------------
    web.post('/chats',chats.post),
    web.get('/chats',chats.get),
    # ---------------------------
    # Список контактов
    # ---------------------------
    web.post('/contacts',contacts.post),
    web.get('/contacts',contacts.get),
    # ---------------------------
    # Список заглушек
    # ---------------------------
    web.post('/plug',plug.post),
    web.get('/plug',plug.get),
    # ---------------------------
    # Список знаний
    # ---------------------------
    web.post('/intent',intent.post),
    web.get('/intent',intent.get),

    web.post('/template',template.post),
    web.get('/template',template.get),


    web.post('/nlp',nlp.post),
    
    web.post('/option',option.post),
    web.get('/option',option.get),

]
