from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/new', method=['POST'])
def neww():
    content = request.get_json()
    print(content)
    return str(content)


if __name__ == '__main__':
    app.run()
