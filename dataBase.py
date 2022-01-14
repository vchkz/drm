# Файл для работы с базой данных
import sqlite3

con = sqlite3.connect('database.db', check_same_thread=False)
cursor = con.cursor()


# Добавление данных

# Добавление серийного номера в таблицу серийных номеров
def add_serial_number(serial_number):
    cursor.execute('''INSERT INTO serial_numbers (serial_number) VALUES (?)''',
                   (serial_number,))
    con.commit()


# Добавление данных, полученных с сервера
def add_data(data):
    # Сделаю после получения данных
    pass


# Добавление пользователя
def add_user(user_type, login, password):
    try:
        cursor.execute('''INSERT INTO users (type, login, password) VALUES (?, ?, ?)''',
                       (user_type, login, password))
        con.commit()
    except:
        print('проблемка')


# Добавить в таблицу доступов, что пользователь с логином user_login может просматривать данные
# по серийному номеру serial_number
def add_access(user_login, serial_number):
    user_id = get_user_id(user_login)
    serial_number_id = get_serial_number_id(serial_number)
    cursor.execute('''INSERT INTO access (user_id, serial_number) VALUES(?, ?)''',
                   (user_id, serial_number_id))
    con.commit()


# Получение данных

# Получить пользователя из таблицы пользователей
# Возвращает данные в порядке id, тип пользователя (админ или не админ), логин, пароль
def get_user(id):
    return cursor.execute('''SELECT * FROM users WHERE id=?''',
                          (id,)).fetchone()[0]


# Получить всех пользователей в системе
# Вернёт список пользователей, каждый элемент списка как в предыдущей функции
def get_users():
    return cursor.execute('''SELECT * FROM users''').fetchall()


# Получить серийный номер по id
def get_serial_number(id):
    return cursor.execute('''SELECT serial_number FROM serial_numbers WHERE id=?''',
                          (id,)).fetchone()[0]


# Получить список серийных номеров, доступных пользователю
# Возвращает список id серийных номеров
def get_serial_numbers_access(user_id):
    return list(map(lambda x: x[0],
                    cursor.execute('''SELECT serial_number FROM access WHERE user_id=?''',
                                   (user_id,)).fetchall()))


# Получить id пользователя по его логину
def get_user_id(user_login):
    return cursor.execute('''SELECT id FROM users WHERE login=?''',
                          (user_login,)).fetchone()[0]


# Получить id серийного номера по серийному номеру
def get_serial_number_id(serial_number):
    return cursor.execute('''SELECT id FROM serial_numbers WHERE serial_number=?''',
                          (serial_number,)).fetchone()[0]


# Получить данные, полученные с сайта по серийному номеру
# Возвращает список данных о серийном номере
# Каждый элемент в формате, как в csv файле, начиная с 1 индекса
# 0-ой индекс каждого элемента - серийный номер
def get_data(serial_number):
    return cursor.execute('''SELECT * FROM data WHERE serial_number=?''',
                          (serial_number,)).fetchall()