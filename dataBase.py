# Файл для работы с базой данных
import sqlite3


con = sqlite3.connect('database.db')
cursor = con.cursor()


# Добавление данных

def add_serial_number(serial_number):
    cursor.execute('''INSERT INTO serial_numbers (serial_number) VALUES (?)''',
                   (serial_number,))
    con.commit()


def add_data(data):
    # Сделаю после получения данных
    pass


def add_user(user_type, login, password):
    cursor.execute('''INSERT INTO users (type, login, password) VALUES (?, ?, ?)''',
                   (user_type, login, password))
    con.commit()


def add_access(user_login, serial_number):
    user_id = get_user_id(user_login)
    serial_number_id = get_serial_number_id(serial_number)
    cursor.execute('''INSERT INTO access (user_id, serial_number) VALUES(?, ?)''',
                   (user_id, serial_number_id))
    con.commit()


# Получение данных

def get_user(id):
    return cursor.execute('''SELECT * FROM users WHERE id=?''',
                          (id,)).fetchone()[0]


def get_serial_number(id):
    return cursor.execute('''SELECT serial_number FROM serial_numbers WHERE id=?''',
                          (id,)).fetchone()[0]


def get_user_id(user_login):
    return cursor.execute('''SELECT id FROM users WHERE login=?''',
                          (user_login,)).fetchone()[0]


def get_serial_number_id(serial_number):
    return cursor.execute('''SELECT id FROM serial_numbers WHERE serial_number=?''',
                          (serial_number,)).fetchone()[0]


# Пока не уверен, что сюда передавать
def get_data():
    pass
