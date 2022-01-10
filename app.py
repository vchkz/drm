from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello BREAD!'


if __name__ == '__main__':
    app.run()
