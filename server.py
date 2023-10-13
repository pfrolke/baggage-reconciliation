from flask import Flask

app = Flask(__name__)


@app.route("/nfc")
def hello_world():
    print('GESCANNED')
    return '<html>HELLO</html>'
