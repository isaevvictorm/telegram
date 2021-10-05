#!/bin/bash

cd /var/www/telegram/
git pull git@github.com:isaevvictorm/telegram.git main
pm2 delete telegram
pm2 start "python3.8 main.py" --name=telegram
