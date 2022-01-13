from flask import Flask, request, render_template
import csv
import io

app = Flask(__name__)


@app.route('/')
def main():
    return render_template("login_main.html")\

@app.route('/user')
def user_page():
    return 'user page'


@app.route('/upload/<serial_number>', methods=['POST'])
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
