from flask import Flask, request, render_template, flash, url_for, session, redirect, abort
import csv
import io
import dataBase
from flask_login import LoginManager, login_required, logout_user, current_user
from log_in import UserLogin

app = Flask(__name__)
app.config["SECRET_KEY"] = "fhmvsktf678"

login_manager = LoginManager(app)
login_manager.login_view = "contact"
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dataBase)


@app.route('/')  # Главная
def main():
    return render_template("Cont.html")


@app.route('/contact', methods=["POST", "GET"])  # вход пользователя
def contact():
    if request.method == "POST":
        if len(request.form["username"]) >= 4 and len(request.form["psw"]) > 4 and "userLogged" in session:
            return redirect(url_for("user", username=session["userLogged"]))
        elif request.method == "POST" and request.form["username"] == "test" and request.form["psw"] == "test":
            session["userLogged"] = request.form["username"]
            return redirect(url_for("admin_page", username=session["userLogged"]))
        else:
            flash("Ошибка")
    return render_template("Cont.html")


@app.route("/logout")  # выход из профиля
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for("contact"))


@app.route('/user/<username>')  # Страница пользователя
@login_required
def user(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f"""<p><a href="{url_for("logout")}">Выйти из профиля</a>
                <p>user info: {current_user.get_id()}"""


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
