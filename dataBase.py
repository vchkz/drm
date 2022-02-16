# Файл для работы с базой данных
import psycopg2


con = psycopg2.connect(user='yxqolserdjwcui',
                       password='5885794dc38490416fceae5aed92ab1e3490b55da36edb6a4ff803231fa883f5',
                       host='ec2-52-214-125-106.eu-west-1.compute.amazonaws.com',
                       port='5432',
                       database='dftlrkkpfa339h')
cursor = con.cursor()


# Добавление данных

# Добавление серийного номера в таблицу серийных номеров
def add_serial_number(serial_number):
    cursor.execute('''INSERT INTO serial_numbers (serial_number) VALUES (%s)''',
                   (serial_number,))
    con.commit()


# Добавление данных, полученных с сервера по серийному номеру
# data - список списков, полученных из csv.reader
def add_data(serial_number_id, data):
    for line in data:
        line = [str(serial_number_id)] + [i if i != '' else 'None' for i in line]
        line[1] = '"' + line[1] + '"'
        line[2] = '"' + line[2] + '"'
        line = ', '.join(line)
        cursor.execute('''INSERT INTO data VALUES ({})'''.format(line))
    con.commit()


# Добавление пользователя
def add_user(user_type, login, password):
    cursor.execute('''INSERT INTO users (type, login, password) 
    VALUES (%s, %s, %s)''', (user_type, login, password))
    con.commit()


# Добавить в таблицу доступов, что пользователь с логином user_login может просматривать данные
# по серийному номеру serial_number
def add_access(user_login, serial_number):
    user_id = get_user_id(user_login)
    serial_number_id = get_serial_number_id(str(serial_number))
    cursor.execute('''INSERT INTO access (user_id, serial_number) VALUES(%s, %s)''',
                   (user_id, serial_number_id))
    con.commit()


# Получение данных

# Получить пользователя из таблицы пользователей
# Возвращает данные в порядке id, тип пользователя (админ или не админ), логин, пароль
def get_user(id):
    cursor.execute('''SELECT * FROM users WHERE id=%s''', (id,))
    return cursor.fetchone()


# Получить всех пользователей в системе
# Вернёт список пользователей, каждый элемент списка как в предыдущей функции
def get_users():
    cursor.execute('''SELECT * FROM users''')
    return cursor.fetchall()


# Получить серийный номер по id
def get_serial_number(id):
    cursor.execute('''SELECT serial_number FROM serial_numbers WHERE id=%s''', (id,))
    return cursor.fetchone()[0]


# Получить список серийных номеров, доступных пользователю
# Возвращает список id серийных номеров
def get_serial_numbers_access(user_id):
    cursor.execute('''SELECT serial_number FROM access WHERE user_id=%s''',
                   (user_id,))
    return list(map(lambda x: x[0], cursor.fetchall()))


# Получить id пользователя по его логину
def get_user_id(user_login):
    cursor.execute('''SELECT id FROM users WHERE login=%s''',
                          (user_login,))
    return cursor.fetchone()[0]


# Получить id серийного номера по серийному номеру
def get_serial_number_id(serial_number):
    serial_number = str(serial_number)
    cursor.execute('''SELECT id FROM serial_numbers WHERE serial_number=%s''',
                          (serial_number,))
    return cursor.fetchone()[0]


# Получить данные, полученные с сайта по серийному номеру
# Возвращает список данных о серийном номере
# Каждый элемент в формате, как в csv файле, начиная с 1 индекса
# 0-ой индекс каждого элемента - серийный номер
def get_data(serial_number_id):
    cursor.execute('''SELECT * FROM data WHERE serial_number=%s''', (serial_number_id,))
    return cursor.fetchall()


# Удаление данных

# Удалить доступ пользователя к определённому серийному номеру
def del_access(user_id, serial_number_id):
    cursor.execute('''DELETE FROM access WHERE user_id=%s and serial_number=%s''',
                   (user_id, serial_number_id))
    con.commit()
