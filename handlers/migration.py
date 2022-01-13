from .modules import DB
import os
import io

def migration():
    db = DB()

    # ----------------------
    # Таблица "Настройки"
    # ----------------------
    db.exec('''
        CREATE TABLE "Setting" (
            name TEXT PRIMARY KEY,
            description TEXT,
            value TEXT NOT NULL,
            type TEXT default 'text' NOT NULL,
            date_insert datetime default current_timestamp
        );
    ''')
    # ----------------------
    # Таблица "Роли"
    # ----------------------
    db.exec('''
        CREATE TABLE "Role" (
            id_role TEXT PRIMARY KEY,
            name_role TEXT NOT NULL,
            description TEXT,
            date_insert datetime default current_timestamp
        );
    ''')

    db.exec('''
        INSERT INTO Role (id_role, name_role, description)
        Select
            '1' as id_role,
            'Администратор' as name_role,
            'Администратор системы' as description
        WHERE NOT EXISTS (SELECT * FROM Role WHERE id_role = 1);
    ''')

    db.exec('''
        INSERT INTO Role (id_role, name_role, description)
        Select
            '2' as id_role,
            'Менеджер' as name_role,
            'Менеджер системы' as description
        WHERE NOT EXISTS (SELECT * FROM Role WHERE id_role = 2);
    ''')

    db.exec('''
        INSERT INTO Role (id_role, name_role, description)
        Select
            '3' as id_role,
            'Оператор' as name_role,
            'Оператор системы' as description
        WHERE NOT EXISTS (SELECT * FROM Role WHERE id_role = 3);
    ''')

    # ----------------------
    # Таблица "Пользователи"
    # ----------------------
    db.exec('''
        CREATE TABLE "User" (
            login TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            id_role INTEGER NOT NULL,
            date_remove datetime,
            date_insert datetime default current_timestamp,
            FOREIGN KEY(id_role) REFERENCES Role(id_role)
        );
    ''')
    
    # ----------------------
    # Добавляем учетные записи по умолчанию
    # ----------------------
    db.exec('''
        INSERT INTO User (login, password, first_name, last_name, id_role)
        Select
            'admin' as login,
            '835d5b87c6d3dcfb686b6ea6f63985265d39826fd6aff8ef0d8539808f9a424d' as password,
            'Администратор' as first_name,
            'Системы' as last_name,
            1 as id_role
        WHERE NOT EXISTS (SELECT * FROM User WHERE id_role = 1);
    ''')

    db.exec('''
        INSERT INTO User (login, password, first_name, last_name, id_role)
        Select
            'manager' as login,
            '835d5b87c6d3dcfb686b6ea6f63985265d39826fd6aff8ef0d8539808f9a424d' as password,
            'Менеджер' as first_name,
            'Системы' as last_name,
            2 as id_role
        WHERE NOT EXISTS (SELECT * FROM User WHERE id_role = 2);
    ''')

    db.exec('''
        INSERT INTO User (login, password, first_name, last_name, id_role)
        Select
            'operator' as login,
            '835d5b87c6d3dcfb686b6ea6f63985265d39826fd6aff8ef0d8539808f9a424d' as password,
            'Оператор' as first_name,
            'Системы' as last_name,
            3 as id_role
        WHERE NOT EXISTS (SELECT * FROM User WHERE id_role = 3);
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
            username TEXT NOT NULL,
            phone_number TEXT,
            city TEXT,
            email TEXT,
            skype TEXT,
            date INTEGER,
            online INTEGER default 0,
            date_insert datetime default current_timestamp
        );
    ''')

    # ----------------------
    # Таблица "Чаты"
    # ----------------------
    #db.exec('''
    #    CREATE TABLE "Chat" (
    #        chat_id TEXT PRIMARY KEY,
    #        first_name TEXT,
    #        last_name TEXT,
    #        username TEXT,
    #        type TEXT,
    #        date INTEGER,
    #        date_insert datetime default current_timestamp
    #    );
    #''')

    # ----------------------
    # Таблица "Сообщения"
    # ----------------------
    db.exec('''
        CREATE TABLE "Message" (
            rid INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT,
            message_id INTEGER,
            from_user__id TEXT NOT NULL,
            chat__id TEXT,
            text TEXT NOT NULL,
            from_me INTEGER,
            date INTEGER,
            caption TEXT,
            file_id TEXT,
            file_unique_id TEXT,
            answer_for text,
            date_answer datetime,
            date_insert datetime default current_timestamp,
            FOREIGN KEY(from_user__id) REFERENCES Contact(user_id)
        );
    ''')

    # ----------------------
    # Таблица "Интенты"
    # ----------------------
    db.exec('''
        CREATE TABLE "Intent" (
            id_intent INTEGER PRIMARY KEY AUTOINCREMENT,
            name_intent TEXT NOT NULL,
            date_insert datetime default current_timestamp
        );
    ''')

    # ----------------------
    # Таблица "Примеры"
    # ----------------------
    db.exec('''
        CREATE TABLE "Example" (
            id_example INTEGER PRIMARY KEY AUTOINCREMENT,
            text_example TEXT NOT NULL,
            id_intent INTEGER NOT NULL,
            date_insert datetime default current_timestamp,
            FOREIGN KEY(id_intent) REFERENCES Intent(id_intent)
        );
    ''')

    # ----------------------
    # Таблица "Ответы"
    # ----------------------
    db.exec('''
        CREATE TABLE "Answer" (
            id_answer INTEGER PRIMARY KEY AUTOINCREMENT,
            text_answer TEXT NOT NULL,
            id_intent INTEGER NOT NULL,
            date_insert datetime default current_timestamp,
            FOREIGN KEY(id_intent) REFERENCES Intent(id_intent)
        );
    ''')

    # ----------------------
    # Таблица "Тип заглушек"
    # ----------------------
    db.exec('''
        CREATE TABLE "Type_plug" (
            id_type INTEGER PRIMARY KEY AUTOINCREMENT,
            name_type TEXT NOT NULL,
            description_type TEXT,
            date_insert datetime default current_timestamp
        );
    ''')

    db.exec('''
        INSERT INTO Type_plug (id_type, name_type, description_type)
        Select
            '1' as id_type,
            'Нет ответа' as name_type,
            'Отправляется если бот не нашел ответ на сообщение пользователя.' as description_type
        WHERE NOT EXISTS (SELECT id_type FROM Type_plug WHERE id_type = 1);
    ''')

    db.exec('''
        INSERT INTO Type_plug (id_type, name_type, description_type)
        Select
            '2' as id_type,
            'Приветствие' as name_type,
            'Отправляется если пользователь отправил команду /start.' as description_type
        WHERE NOT EXISTS (SELECT id_type FROM Type_plug WHERE id_type = 2);
    ''')

    db.exec('''
        INSERT INTO Type_plug (id_type, name_type, description_type)
        Select
            '3' as id_type,
            'Контакт' as name_type,
            'Отправляется если пользователь поделился контактными данными.' as description_type
        WHERE NOT EXISTS (SELECT id_type FROM Type_plug WHERE id_type = 3);
    ''')

    # ----------------------
    # Таблица "Заглушек"
    # ----------------------
    db.exec('''
        CREATE TABLE "Plug" (
            rid INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            id_type INTEGER NOT NULL,
            date_insert datetime default current_timestamp,
            FOREIGN KEY(id_type) REFERENCES Type_plug(id_type)
        );
    ''')

    # ----------------------
    # Таблица "Template"
    # ----------------------
    db.exec('''
        CREATE TABLE "Template" (
            id_template INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            response TEXT NOT NULL,
            flag_correct INTEGER default 1,
            date_insert datetime default current_timestamp
        );
    ''')

    # ----------------------
    # Таблица "IMG"
    # ----------------------
    #db.exec('''
    #    CREATE TABLE "Image" (
    #        id_img INTEGER PRIMARY KEY AUTOINCREMENT,
    #        path TEXT,
    #        id_response INTEGER,
    #        date_insert datetime default current_timestamp,
    #        FOREIGN KEY(id_response) REFERENCES Response(id_response)
    #    );
    #''')