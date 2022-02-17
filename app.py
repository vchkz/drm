from flask import Flask, request, render_template, flash, redirect, session
import csv
import io
import datetime
import dataBase
from flask_login import LoginManager, login_required, logout_user, UserMixin, login_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "fhmvsktf678"

login_manager = LoginManager(app)

class User(UserMixin):
    pass


@app.route('/', methods=["POST", "GET"])  # Главная
def main():
    if request.method == "POST":
        username = request.form['username']
        try:
            passwordVerif = dataBase.get_user(dataBase.get_user_id(username))[3]
        except:
            passwordVerif = None

        if request.form['password'] == passwordVerif:
            user = User()
            user.id = username
            login_user(user)
            if dataBase.get_user(dataBase.get_user_id(username))[1] == 0:
                return redirect('/user')
            else:
                return redirect('/admin')
        else:
            flash("Неверный логин или пароль", "success")
            return redirect('/')

    # авторизованного пользователея перебрасывает на /user или /admin ели он пытается зайти на главную
    try:
        username = session['_user_id']
        if dataBase.get_user(dataBase.get_user_id(username))[1] == 0:
            return redirect('/user')
        else:
            return redirect('/admin')
    except:
        pass

    return render_template("Cont.html")


@login_manager.user_loader
def user_loader(user_id):
    user = User()
    user.id = user_id
    return user


@app.route("/logout")  # выход из профиля
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect('/')


@app.route('/user')  # Страница пользователя
@login_required
def user():
    username = session['_user_id']

    serial_numbers = list(map(lambda x: dataBase.get_serial_number(x),
                              dataBase.get_serial_numbers_access(dataBase.get_user_id(username))))
    return render_template("user_page.html", username=username, serial_numbers=serial_numbers)


@app.route('/aesc/<aesc_serial_number>')  # Страница конкретной АКЭС
@login_required
def aesc(aesc_serial_number):
    labels = []
    values = []
    zz = []
    username = session['_user_id']
    serial_numbers = list(map(lambda x: str(dataBase.get_serial_number(x)),
                              dataBase.get_serial_numbers_access(dataBase.get_user_id(username))))

    if aesc_serial_number not in serial_numbers:
        error = "У вас нет доступа к этому АКЭС"
        return render_template("error.html", error=error)

    week = request.args.get('week')
    day = request.args.get('day')
    id_serial_number = dataBase.get_serial_number_id(int(aesc_serial_number))
    if day:
        day = day.split('-')[2] + '.' + day.split('-')[1] + '.' + day.split('-')[0]
        data = [i for i in dataBase.get_data(id_serial_number) if str(i[1].split()[0]) == day]
        # data - это данные за определённый день
        if data == []:
            err = f'За {day} нет данных'
            return render_template("aesc_page.html", username=username, serial_number=aesc_serial_number, err=err)
        for elem in data:
            if elem[16] == None:
                n = '-'
            else:
                labels.append(elem[1])
                Pon = float(elem[6]) + float(elem[7]) + float(elem[8])  # сумма активной мощности при включенной системе
                Poff = float(elem[18]) + float(elem[19]) + float(elem[20])
                # Poff - сумма активной мощности по каждой фазе при выключенной системе
                n = round((Poff - Pon) / Poff * 100, 1)  # эффективность
                values.append(int(n))
            zz.append(n)

        is_data = True
        if not labels:
            is_data = False
        return render_template('data.html', labels=labels, values=values, period=day, is_data=is_data,
                               data=zip(data, zz))

    if week:
        n_week = datetime.datetime.strptime(week + '-1', '%G-W%V-%u').toordinal()
        k_week = datetime.datetime.strptime(week + '-7', '%G-W%V-%u').toordinal()
        start_week = datetime.datetime.strptime(week + '-1', '%G-W%V-%u')
        end_week = datetime.datetime.strptime(week + '-7', '%G-W%V-%u')
        period = 'C ' + start_week.strftime("%d.%m.%Y") + ' по ' + end_week.strftime("%d.%m.%Y")
        data = ([i for i in dataBase.get_data(id_serial_number) if
                 n_week <= datetime.datetime.strptime(i[1].split()[0], "%d.%m.%Y").toordinal() <= k_week])
        print(data)
        data.sort(key=lambda x: datetime.datetime.strptime(x[1].split()[0], "%d.%m.%Y").toordinal())
        # data - это данные за определённую неделю
        if data == []:
            err = f'За период {period} нет данных'
            return render_template("aesc_page.html", username=username, serial_number=aesc_serial_number, err=err)

        for elem in data:
            if elem[16] == None:
                n = '-'
            else:

                labels.append(elem[1])
                Pon = float(elem[6]) + float(elem[7]) + float(elem[8])  # сумма активной мощности при включенной системе
                Poff = float(elem[18]) + float(elem[19]) + float(elem[20])
                # Poff - сумма активной мощности по каждой фазе при выключенной системе
                n = round((Poff - Pon) / Poff * 100, 1)  # эффективность
                values.append(int(n))
            zz.append(n)

        is_data = True
        if not labels:
            is_data = False
        return render_template('data.html', labels=labels, values=values, period=period, is_data=is_data,
                               data=zip(data, zz))

    return render_template("aesc_page.html", username=username, serial_number=aesc_serial_number)


@app.route('/admin/delete-serial-number', methods=['POST'])  # Вспомогательная страница (Зайти сюда нельзя)
def delete_serial_number():
    if request.method == 'POST':
        del_sernum = request.form['delete_sernum']
        del_sernum = del_sernum[1:-1].split(', ')
        login = del_sernum[0][1:-1]
        ser_num = str(del_sernum[1])[1:-1]
        dataBase.del_access(dataBase.get_user_id(login), dataBase.get_serial_number_id(ser_num))
    return redirect('/admin')


@app.route('/admin', methods=['GET', 'POST'])  # Страница админа
@login_required
def admin_page():
    if request.method == 'POST':
        new_serial_number = request.form['ser_num']
        to_user = request.form['user']
        try:
            dataBase.add_serial_number(new_serial_number)
        except:
            pass

        try:
            if dataBase.get_serial_number_id(new_serial_number) \
                    not in dataBase.get_serial_numbers_access(dataBase.get_user_id(to_user)):
                dataBase.add_access(to_user, new_serial_number)
            else:
                return '''
                      <h1>Ошибка</h1>
                      <h3>У данного пользователя уже есть доступ к этому АКЭС</h3>
                      <a href="/admin">Вернуться назад</a>
                      '''
        except:
            pass

        return redirect('/admin')

    user_list_admin_page = [(list(map(lambda x: dataBase.get_serial_number(x),
                                      dataBase.get_serial_numbers_access(i[0]))), i[2])
                            for i in dataBase.get_users() if not i[1]]

    if dataBase.get_user(dataBase.get_user_id(session['_user_id']))[1] == 0:
        error = "У вас нет доступа к странице администратора"
        return render_template("error.html", error=error)

    return render_template("admin_page.html", user_list_admin_page=user_list_admin_page)


@app.route('/admin/new-user', methods=['GET', 'POST'])  # Страница создания нового пользователя
def create_user():
    if request.method == 'POST':
        new_login = request.form['new_login']
        new_password = request.form['psw']
        new_serial_number = request.form['serial_number']

        if new_login not in list(map(lambda x: x[2], dataBase.get_users())):
            dataBase.add_user(0, new_login, new_password)
        else:
            return '''
                  <h1>Ошибка</h1>
                  <h3>Пользователь с таким логином уже существует</h3>
                  <a href="/admin/new-user">Вернуться назад</a>
                  '''
        try:
            dataBase.add_serial_number(new_serial_number)
        except:
            pass

        dataBase.add_access(new_login, new_serial_number)

        return redirect('/admin')

    return render_template("create_user.html")


@app.route('/upload/<serial_number>', methods=['POST'])  # Страница загрузки файла
def profile(serial_number):
    file = io.StringIO(request.files['file'].stream.read().decode("UTF-8"), newline=None)
    reader = csv.reader(file, delimiter=';')
    data = list(reader)
    print(data)
    try:
        print(dataBase.get_serial_number_id(serial_number))
    except:
        dataBase.add_serial_number(serial_number)
        print('новый детектед')

    dataBase.add_data(dataBase.get_serial_number_id(serial_number), data)

    return 'success'


@app.errorhandler(404)
def pageNotFound(error):  # несуществующая страницы
    return render_template("404.html"), 404


@app.errorhandler(401)
def Unauthorized(error):
    return '<h1>Нет доступа</h1>'


if __name__ == '__main__':
    app.run(debug=True)
