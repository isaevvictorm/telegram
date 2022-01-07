# Скачиваем репозиторий с git в папку /var/www/проект/
```python
sudo git init
ssh-keygen -t ed25519 -C "isaevvictorm@example.com"
eval `ssh-agent -s`
ssh-add
git pull git@github.com:isaevvictorm/telegram.git main
```
# Автоматическая установка из /var/www/проект/
chmod +x install.sh
./install.sh
chmod +x restart

# Сертификат NGNIX
https://www.digitalocean.com/community/tutorials/nginx-let-s-encrypt-ubuntu-18-04-ru

# Первые шаги
1. Копируем файл "config_default.json" и переименовываем его в "config.json"
2. Создаем бота чрез @BotFather
3. Указываем токен и имя бота в файле "config.json"

# Запускаем проект из /var/www/проект/
/var/www/telegram/restart

# Пример конфига NGINX
server{
	listen 443 ssl;
	listen [::]:443;

	root /var/www/html;
	server_name example.ru www.example.ru;

	location / {
		proxy_connect_timeout 9999s;
		proxy_read_timeout 9999s;
		client_max_body_size 1000M;
		proxy_pass http://127.0.0.1:8443/;
	}
}