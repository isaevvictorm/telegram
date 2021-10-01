from handlers import setting, migration
import aiohttp_jinja2
import jinja2
from aiohttp import web
from routes import routes
import ssl
import os
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
result = migration.migration()

# -============================
# - Проверяем наличие сертификата
# - и создаем его если нет
# -============================
if not os.path.exists(os.path.join(os.getcwd() + "/", setting["WEBHOOK_SSL_CERT"])):
    os.system('openssl req -newkey rsa:2048 -sha256 -nodes -keyout webhook_pkey.key -x509 -days 365 -out webhook_cert.pem -subj "/C=US/ST=Moscow/L=Moscow/O=bot/CN={0}"'.format(setting['SERVER_IP']))

# -============================
# - Указываем путь к шаблонам
# -============================
aiohttp_jinja2.setup(app, loader = jinja2.FileSystemLoader(setting["TEMPLATE_DIR"]))

# -===========================================
# - Указываем роуты и пути к файлам со стилями
# -===========================================
app.add_routes(routes)
app.router.add_static('/static', pathlib.Path(os.getcwd() + '/static'), show_index = True)

try:
    # -============================
    # - Добавляем сертификат
    # -============================
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(os.path.join(os.getcwd() + "/", setting["WEBHOOK_SSL_CERT"]), os.path.join(os.getcwd() + "/", setting["WEBHOOK_SSL_PRIV"]))
    web.run_app(
        make_app(app),
        host=setting["WEBHOOK_HOST"],
        port=setting["WEBHOOK_PORT"],
        ssl_context=context,
    )
except:
    # -============================
    # - Без сертификата
    # -============================
    try:
        web.run_app(
            make_app(app),
            host=setting["WEBHOOK_HOST"],
            port=setting["WEBHOOK_PORT"],
        )
    except Exception as ee:
        print("Error: ", str(ee))
