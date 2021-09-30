import json
import os

setting = None
try:
    print('Setting:', os.path.join(os.getcwd() + "/", "config.json"))
    with open(os.path.join(os.getcwd() + "/", "config.json")) as f:
        setting = json.load(f)
except Exception as ee:
    print("Error: Не удалось получить файл настроек ({0})".format(str(ee)))
