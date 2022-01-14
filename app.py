from flask import Flask, request, render_template, flash, url_for, session, redirect
import csv
import io
import dataBase

app = Flask(__name__)
app.config["SECRET_KEY"] = "fhmvsktf678"


@app.route('/')  # Главная
def main():
    return render_template("Cont.html")


@app.route('/contact', methods=["POST", "GET"])  # вход пользователя
def contact():
    if request.method == "POST":
        if len(request.form["email"]) >= 4 and len(request.form["psw"]) > 2:
            flash("Авторизация выполнена")
        else:
            flash("Ошибка")
    return render_template("Cont.html")


@app.route('/user/<username>')  # Страница пользователя
def user(username):
    return f"Профиль пользователя: {username}"


@app.route('/admin')  # Страница админа
def admin_page():
    user_list_admin_page = [((str(i[0])), i[2]) for i in dataBase.get_users() if not i[1]]
    # print(dataBase.get_serial_numbers_access(7))
    return render_template("admin_page.html", user_list_admin_page=user_list_admin_page)


@app.route("/login", methods=["POST", "GET"])
def login():
    if 'userLogged' in session:
        return redirect(url_for('user', username=session['userLogged']))
    elif request.form['username'] == "test" and request.form['psw'] == "test":
        session['userLogged'] = request.form['email']
        return redirect(url_for('admin', username=session['userLogged']))

    return render_template('login_main.html', title="Авторизация")


@app.route('/admin/new-user', methods=['GET', 'POST'])  # Страница создания нового пользователя
def create_user():
    if request.method == 'POST':
        new_login = request.form['new_login']
        new_password = request.form['psw']
        new_serial_number = request.form['serial_number']
        dataBase.add_user(0, new_login, new_password)
        dataBase.add_serial_number(new_serial_number)
        dataBase.add_access(new_login, new_serial_number)
        return redirect('/')

    return render_template("create_user.html")


@app.route('/upload/<serial_number>', methods=['POST'])  # Страница загрузки файла
def profile(serial_number):
    file = io.StringIO(request.files['file'].stream.read().decode("UTF-8"), newline=None)
    reader = csv.reader(file, delimiter=';')
    for line in reader:
        print(line)  # тут будут выводиться принятые данные в виде списка
    print(serial_number)  # тут будет выводиться серийный номер АКЭС

    #     отправить файл.csv можно через коммандную строку:
    #     curl -F "file=@example.csv" http://localhost:5000/upload/<Здесь будет серийный номер>

    return 'success'


@app.errorhandler(404)
def pageNotFound(error):  # поиск не существующей страницы
    return render_template("404.html"), 404


if __name__ == '__main__':
    app.run(debug=True)
