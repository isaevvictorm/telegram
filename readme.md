# Скачиваем репозиторий с git в папку /var/www/проект/
```python
sudo git init
ssh-keygen -t ed25519 -C "isaevvictorm@example.com"
eval `ssh-agent -s`
ssh-add
git pull git@github.com:isaevvictorm/telegram.git main
```

# Сертификат NGNIX
sudo systemctl stop nginx
cd /var/www/telegram/startup/golang/LetsEncryptHandler
./LetsEncryptHandler
rm ./certs/your_domain.ru
curl https://your_domain.ru
[ctrl+c]
systemctl start nginx

# Автоматическая установка из /var/www/проект/
chmod +x install.sh
./install.sh
chmod +x restart

# Первые шаги
1. Копируем файл "config_default.json" и переименовываем его в "config.json"
2. Создаем бота чрез @BotFather
3. Указываем токен и имя бота в файле "config.json"

# Запускаем проект из /var/www/проект/
/var/www/telegram/restart
