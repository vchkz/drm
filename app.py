from flask import Flask, request
import csv
import io

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, this is the WHITE BREAD page'


@app.route('/serial_number_will_be_here', methods=['POST'])
def upload():
    file = io.StringIO(request.files['file'].stream.read().decode("UTF-8"), newline=None)
    reader = csv.reader(file, delimiter=';')
    for line in reader:
        print(line) # тут будут выводиться принятые данные в виде списка

    #     отправить файл.csv можно через коммандную сторку:
    #     curl -F "file=@example.csv" http://localhost:5000/serial_number_will_be_here

    return 'success'


if __name__ == '__main__':
    app.run(debug=True)
