#!/bin/bash
echo "Разворачиваем необходимое ПО (Python3.8, необходимые библиотеки и др.)"

sudo apt update -y
sudo apt install nginx -y
sudo ufw allow 'Nginx Full'
sudo apt install golang -y

sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y

sudo apt install python3.8 -y
sudo apt-get install python3-pip -y
sudo apt-get install python3.8-dev -y

python3.8 -m pip install --upgrade pip
python3.8 -m pip install aiohttp
python3.8 -m pip install cchardet
python3.8 -m pip install aiodns
python3.8 -m pip install pyTelegramBotAPI
python3.8 -m pip install pysqlite3
python3.8 -m pip install asyncio
python3.8 -m pip install requests
python3.8 -m pip install aiohttp_jinja2
python3.8 -m pip install aiohttp_session
python3.8 -m pip install jinja2
python3.8 -m pip install pathlib
python3.8 -m pip install cryptography

sudo apt install nodejs -y
sudo apt install npm -y

echo "Устанавливаем PM2"
sudo npm install pm2 -g
