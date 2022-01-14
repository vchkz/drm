from flask import Flask, request, render_template, redirect
import csv
import io
import dataBase

app = Flask(__name__)


@app.route('/')  # Главная
def main():
    return render_template("login_main.html")


@app.route('/user')  # Страница пользователя
def user_page():
    return 'user page'


@app.route('/admin')  # Страница админа
def admin_page():
    user_list_admin_page = [((str(i[0])), i[2]) for i in dataBase.get_users() if not i[1]]
    # print(dataBase.get_serial_numbers_access(7))
    return render_template("admin_page.html", user_list_admin_page=user_list_admin_page)


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


if __name__ == '__main__':
    app.run(debug=True)
