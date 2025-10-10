import sqlite3

class SQLiteDatabase:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
