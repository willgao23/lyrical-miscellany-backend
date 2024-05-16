from flask import Flask
from lyricsgenius import Genius

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"