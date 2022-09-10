import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "user_sheets.db")


def init():
    db = sqlite3.connect(db_path)
    sql = db.cursor()
    sql.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT,
            spreadsheet_id TEXT,
            categories TEXT) 
    ''')
    db.commit()
    print('Initialized Users DB')


def conn():
    return sqlite3.connect(db_path)


def add_user_sheet(user_id, spreadsheet_id, categories=[]) -> bool:
    try:
        connection = conn()
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO users (`user_id`, `spreadsheet_id`, `categories`) VALUES ('{user_id}', '{spreadsheet_id}', '{':'.join(categories)}')")
        connection.commit()
        return True
    finally:
        connection.close()
    