import json
import os
import requests

setting = None
try:
    print('Setting:', os.path.join(os.getcwd() + "/", "config.json"))
    with open(os.path.join(os.getcwd() + "/", "config.json")) as f:
        setting = json.load(f)
except Exception as ee:
    print("Error: ({0})".format(str(ee)))

# -============================
# - Получаем IP - адрес сервера
# -============================
try:
    setting.update({'SERVER_IP': '0.0.0.0'})
    response = requests.get('http://ifconfig.me/ip')
    setting.update({'SERVER_IP': response.content.decode()})
    print('IP-address server:', setting['SERVER_IP'])
except Exception as ee:
    print('IP-address error:', str(ee))

# -============================
# - Проверяем наличие сертификата
# - и создаем его если нет
# -============================
if not os.path.exists(os.path.join(os.getcwd() + "/", setting["WEBHOOK_SSL_CERT"])):
    os.system('openssl req -newkey rsa:2048 -sha256 -nodes -keyout webhook_pkey.key -x509 -days 365 -out webhook_cert.pem -subj "/C=US/ST=Moscow/L=Moscow/O=bot/CN={0}"'.format(setting['DOMEN'] if len(setting['DOMEN']) > 0 else setting['SERVER_IP']))
