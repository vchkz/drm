from flask import Flask, request, render_template, flash, url_for, redirect, session
import csv
import io
import dataBase
from flask_login import LoginManager, login_required, logout_user, current_user, UserMixin, login_user


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


    return render_template("Cont.html")


@login_manager.user_loader
def user_loader(user_id):
    dataBase.get_user(user_id)
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
    # sernum_list =
    # return render_template("admin_page.html", sernum_list=sernum_list)
    return render_template("user_page.html")


@app.route('/admin/delete-serial-number', methods=['POST'])  # Вспомогательная страница (Зайти сюда нельзя)
def delete_serial_number():
    if request.method == 'POST':
        del_sernum = request.form['delete_sernum']
        del_sernum = del_sernum[1:-1].split(', ')
        login = del_sernum[0][1:-1]
        ser_num = int(del_sernum[1])
        print(login, ser_num)
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
                      <h3>У данного пользователя уже есть доступ к этой АКЭС</h3>
                      <a href="/admin">Вернуться назад</a>
                      '''
        except:
            pass

        return redirect('/admin')


    user_list_admin_page = [(list(map(lambda x: dataBase.get_serial_number(x),
                                      dataBase.get_serial_numbers_access(i[0]))), i[2])
                            for i in dataBase.get_users() if not i[1]]

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
    try:
        dataBase.add_serial_number(serial_number)
    except:
        pass  # значит такой серийный номер уже есть
    dataBase.add_data(dataBase.get_serial_number_id(serial_number), data)

    return 'success'


@app.errorhandler(404)
def pageNotFound(error):  # поиск не существующей страницы
    return render_template("404.html"), 404


if __name__ == '__main__':
    app.run(debug=True)