from handlers import migration
import aiohttp_jinja2
import jinja2
from aiohttp import web
import ssl
import os
from handlers import Setting
import pathlib
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_session import setup, get_session

app = web.Application()

def make_app(app):
    setup(app, EncryptedCookieStorage("MlXkDT8Ou5e5EoZ6GcTiDKAHbca0FrMK2sJTcqv429Q="))
    return app

# -============================
# - Создание таблиц БД и их обновление
# -============================
migration.migration()

params = Setting()
setting = params.get()

# -============================
# - Указываем путь к шаблонам
# -============================
aiohttp_jinja2.setup(app, loader = jinja2.FileSystemLoader('./templates'))

# -===========================================
# - Указываем роуты и пути к файлам со стилями
# -===========================================
from routes import routes
app.add_routes(routes)
app.router.add_static('/static', pathlib.Path(os.getcwd() + '/static'), show_index = True)

# -============================
# - Запускаем
# -============================

web.run_app(
    make_app(app),
    port=setting["WEBHOOK_PORT"],
)
