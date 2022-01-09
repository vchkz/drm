from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello WITEBREAD!'


if __name__ == '__main__':
    app.run()
