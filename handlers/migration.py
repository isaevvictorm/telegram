from .modules import DB
import os
import io

def migration():
    db = DB()

    # ----------------------
    # Таблица "Пользователи"
    # ----------------------
    db.exec('''
        CREATE TABLE "User" (
            login TEXT PRIMARY KEY,
            password TEXT,
            first_name TEXT,
            last_name TEXT,
            admin INTEGER,
            date_remove datetime,
            date_insert datetime default current_timestamp
        );
    ''')
    
    # ----------------------
    # Добавляем учетную запись администратора "первого эшелона"
    # ----------------------
    db.exec('''
        INSERT INTO User (login, password, first_name, last_name, admin)
        Select
            'admin' as login,
            '835d5b87c6d3dcfb686b6ea6f63985265d39826fd6aff8ef0d8539808f9a424d' as password,
            'Администратор' as first_name,
            'Admin' as last_name,
            1 as admin
        WHERE NOT EXISTS (SELECT * FROM User WHERE admin = 1);
    ''')

    # ----------------------
    # Таблица "Контакты (Пользователи чата)"
    # ----------------------
    db.exec('''
        CREATE TABLE "Contact" (
            user_id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            patronymic TEXT,
            birthday date,
            username TEXT,
            is_bot TEXT,
            language_code TEXT,
            phone_number TEXT,
            city TEXT,
            email TEXT,
            skype TEXT,
            date INTEGER,
            date_insert datetime default current_timestamp
        );
    ''')

    # ----------------------
    # Таблица "Чаты"
    # ----------------------
    db.exec('''
        CREATE TABLE "Chat" (
            chat_id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            type TEXT,
            date INTEGER,
            date_insert datetime default current_timestamp
        );
    ''')

    # ----------------------
    # Таблица "Сообщения"
    # ----------------------
    db.exec('''
        CREATE TABLE "Message" (
            rid INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT,
            message_id INTEGER,
            from_user__id TEXT,
            is_bot INTEGER,
            chat__id TEXT,
            text TEXT,
            from_me INTEGER,
            date INTEGER,
            caption TEXT,
            file_id TEXT,
            file_unique_id TEXT,
            answer_for text,
            date_answer datetime,
            date_insert datetime default current_timestamp
        );
    ''')

    # ----------------------
    # Таблица "Интенты"
    # ----------------------
    db.exec('''
        CREATE TABLE "Intent" (
            id_intent INTEGER PRIMARY KEY AUTOINCREMENT,
            name_intent TEXT,
            date_insert datetime default current_timestamp
        );
    ''')

    # ----------------------
    # Таблица "Примеры"
    # ----------------------
    db.exec('''
        CREATE TABLE "Example" (
            id_example INTEGER PRIMARY KEY AUTOINCREMENT,
            text_example TEXT,
            id_intent INTEGER,
            date_insert datetime default current_timestamp,
            FOREIGN KEY(id_intent) REFERENCES Intent(id_intent)
        );
    ''')

    # ----------------------
    # Таблица "Заглушек"
    # ----------------------
    db.exec('''
        CREATE TABLE "Failure" (
            rid INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            type TEXT,
            date_insert datetime default current_timestamp
        );
    ''')

    db.exec('''
        ALTER TABLE "Failure" add type TEXT;
    ''')

    # ----------------------
    # Таблица "Ответы"
    # ----------------------
    db.exec('''
        CREATE TABLE "Answer" (
            id_answer INTEGER PRIMARY KEY AUTOINCREMENT,
            text_answer TEXT,
            id_intent INTEGER,
            date_insert datetime default current_timestamp,
            FOREIGN KEY(id_intent) REFERENCES Intent(id_intent)
        );
    ''')

    # ----------------------
    # Таблица "Template"
    # ----------------------
    db.exec('''
        CREATE TABLE "Template" (
            id_template INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            response TEXT,
            flag_correct INTEGER default 1,
            date_insert datetime default current_timestamp
        );
    ''')

    # ----------------------
    # Таблица "IMG"
    # ----------------------
    db.exec('''
        CREATE TABLE "Image" (
            id_img INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT,
            id_response INTEGER,
            date_insert datetime default current_timestamp,
            FOREIGN KEY(id_response) REFERENCES Response(id_response)
        );
    ''')