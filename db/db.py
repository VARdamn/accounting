import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "user_sheets.db")


def init():
    db = sqlite3.connect(db_path)
    sql = db.cursor()
    sql.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            expenses_spreadsheet_id TEXT, 
            incomes_spreadsheet_id TEXT) 
    ''')
    db.commit()
    print('Initialized Users DB')


def conn():
    return sqlite3.connect(db_path)


def is_user_in_db(user_id: str) -> bool:
    try:
        connection = conn()
        cursor = connection.cursor()
        cursor.execute(f"SELECT user_id from users WHERE user_id = '{user_id}'")
        return True if cursor.fetchone()[0] else False
    except:
        return False
    finally:
        connection.close()


def add_user_sheet(user_id: str, spreadsheet_id: str, _type: str) -> bool:
    try:
        connection = conn()
        cursor = connection.cursor()
        if not is_user_in_db(user_id):
            cursor.execute(f"INSERT INTO users (`user_id`, `{_type}_spreadsheet_id`) VALUES ('{user_id}', '{spreadsheet_id}')")
        else:
            cursor.execute(f"UPDATE users SET `{_type}_spreadsheet_id` = '{spreadsheet_id}' WHERE user_id = '{user_id}'")
        connection.commit()
        return True
    finally:
        connection.close()


def get_user_spreadsheet_id(user_id: str, _type: str) -> str | None:
    try:
        connection = conn()
        cursor = connection.cursor()
        cursor.execute(f"SELECT {_type}_spreadsheet_id FROM users WHERE user_id = '{user_id}'")
        return cursor.fetchone()[0]
    except:
        return None
    finally:
        connection.close()


def get_all_users_spreadsheet_ids() -> list:
    try:
        connection = conn()
        # connection.row_factory = lambda cursor, row: row[0]
        cursor = connection.cursor()
        cursor.execute(f"SELECT expenses_spreadsheet_id, incomes_spreadsheet_id from users")
        lst = []
        for el in cursor.fetchall():
            for item in el:
                if not item:
                    continue
                lst.append(item)
        return lst
    except:
        return []
    finally:
        connection.close()
