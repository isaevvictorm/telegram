from aiohttp import web
from handlers import *

routes=[
    web.post('/{token}/', telegram.post),
]
