# Скачиваем репозиторий с git в папку /var/www/проект/
```python
sudo git init
ssh-keygen -t ed25519 -C "isaevvictorm@example.com"
sudo git pull git@github.com:isaevvictorm/telegram.git main
```
# Автоматическая установка из /var/www/проект/
chmod +x install.sh
./install.sh

# Первые шаги
1. Копируем файл "config_default.json" и переименовываем его в "config.json"
2. Создаем бота чрез @BotFather
3. Указываем токен и имя бота в файле "config.json"

# Запускаем проект из /var/www/проект/
```python
pm2 start main.py --interpreter=python3.8
```
