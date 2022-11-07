import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "user_sheets.db")


def init():
    db = sqlite3.connect(db_path)
    sql = db.cursor()
    sql.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT,
            spreadsheet_id TEXT) 
    ''')
    db.commit()
    print('Initialized Users DB')


def conn():
    return sqlite3.connect(db_path)


def add_user_sheet(user_id: str | int, spreadsheet_id: str) -> bool:
    try:
        connection = conn()
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO users (`user_id`, `spreadsheet_id`) VALUES ('{user_id}', '{spreadsheet_id}')")
        connection.commit()
        return True
    finally:
        connection.close()


def get_user_spreadsheet_id(user_id: str | int) -> str | None:
    try:
        connection = conn()
        cursor = connection.cursor()
        cursor.execute(f"SELECT spreadsheet_id from users where user_id = '{user_id}'")
        return cursor.fetchone()[0]
    except:
        return None
    finally:
        connection.close()


def get_all_users_spreadsheet_ids() -> list:
    try:
        connection = conn()
        connection.row_factory = lambda cursor, row: row[0]
        cursor = connection.cursor()
        cursor.execute(f"SELECT spreadsheet_id from users")
        return cursor.fetchall()
    except:
        return []
    finally:
        connection.close()