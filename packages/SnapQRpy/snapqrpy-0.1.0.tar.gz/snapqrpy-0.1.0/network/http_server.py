from flask import Flask

class HTTPServer:
    def __init__(self):
        self.app = Flask(__name__)
