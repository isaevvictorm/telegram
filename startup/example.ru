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