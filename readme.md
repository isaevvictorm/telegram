# Скачиваем репозиторий с git в папку /var/www/проект/
```python
apt-get install git -y
git init
git remote add origin https://github.com/isaevvictorm/telegram.git
git pull https://github.com/isaevvictorm/telegram.git main
```
# Автоматическая установка из /var/www/проект/
chmod +x install.sh
./install.sh

# Запускаем проект из /var/www/проект/
```python
pm2 start main.py --interpreter=python3.8
```

# Первые шаги
1. Для начала работы необходимо добавить бота и его токен
