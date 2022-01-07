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
