from .modules import db

def migration():
    # Таблица "Пользователи"
    db.executescript('''
        CREATE TABLE "User" (
            `login` TEXT PRIMARY KEY,
            `password` TEXT,
            `first_name` TEXT,
            `last_name` TEXT,
            `admin` INTEGER,
            `date_remove` datetime,
            `date_insert` datetime default current_timestamp
        );
    ''', True)

    # Добавляем учетную запись администратора "первого эшелона"
    db.executescript('''
        INSERT INTO User (login, password, first_name, last_name, admin)
        Select
            'admin' as login,
            '835d5b87c6d3dcfb686b6ea6f63985265d39826fd6aff8ef0d8539808f9a424d' as password,
            'Администратор' as first_name,
            'Admin' as last_name,
            1 as admin
        WHERE NOT EXISTS (SELECT * FROM User WHERE admin = 1);
    ''', True)

    # Таблица "Webhook"
    db.executescript('''
        CREATE TABLE "Webhook" (
            `webhook_id` INTEGER PRIMARY KEY,
            `name` TEXT,
            `token` TEXT,
            `admin` TEXT,
            `status` INTEGER,
            `date_insert` datetime default current_timestamp
        );
    ''', True)

    # Таблица "Контакты (Пользователи чата)"
    db.executescript('''
        CREATE TABLE "Contact" (
            `user_id` TEXT PRIMARY KEY,
            `first_name` TEXT,
            `last_name` TEXT,
            `patronymic` TEXT,
            `birthday` date,
            `username` TEXT,
            `is_bot` TEXT,
            `language_code` TEXT,
            `phone_number` TEXT,
            `city` TEXT,
            `email` TEXT,
            `skype` TEXT,
            `date` INTEGER,
            `date_insert` datetime default current_timestamp
        );
    ''')

    # Таблица "Чаты"
    db.executescript('''
        CREATE TABLE "Chat" (
            `chat_id` TEXT PRIMARY KEY,
            `first_name` TEXT,
            `last_name` TEXT,
            `username` TEXT,
            `type` TEXT,
            `date` INTEGER,
            `date_insert` datetime default current_timestamp
        );
    ''')

    # Таблица "Сообщения"
    db.executescript('''
        CREATE TABLE "Message" (
            `rid` INTEGER PRIMARY KEY AUTOINCREMENT,
            `content_type` TEXT,
            `message_id` INTEGER,
            `from_user__id` TEXT,
            `is_bot` INTEGER,
            `chat__id` TEXT,
            `text` TEXT,
            `from_me` INTEGER,
            `date` INTEGER,
            `caption` TEXT,
            `file_id` TEXT,
            `file_unique_id` TEXT,
            `date_answer` datetime,
            `date_insert` datetime default current_timestamp
        );
    ''')

    return True
