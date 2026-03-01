import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'user_sheets.db')


def init() -> None:
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                expenses_spreadsheet_id TEXT,
                incomes_spreadsheet_id TEXT
            )
            '''
        )
        connection.commit()


def conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def is_user_in_db(user_id: str) -> bool:
    with conn() as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
        return cursor.fetchone() is not None


def add_user_sheet(user_id: str, spreadsheet_id: str, sheet_type: str) -> bool:
    if sheet_type not in {'expenses', 'incomes'}:
        raise ValueError('Invalid sheet type')

    column = f'{sheet_type}_spreadsheet_id'
    with conn() as connection:
        cursor = connection.cursor()
        if not is_user_in_db(user_id):
            cursor.execute(
                f'INSERT INTO users (user_id, {column}) VALUES (?, ?)',
                (user_id, spreadsheet_id),
            )
        else:
            cursor.execute(
                f'UPDATE users SET {column} = ? WHERE user_id = ?',
                (spreadsheet_id, user_id),
            )
        connection.commit()
        return True


def get_user_spreadsheet_id(user_id: str, sheet_type: str) -> str | None:
    if sheet_type not in {'expenses', 'incomes'}:
        raise ValueError('Invalid sheet type')

    with conn() as connection:
        cursor = connection.cursor()
        cursor.execute(
            f'SELECT {sheet_type}_spreadsheet_id FROM users WHERE user_id = ?',
            (user_id,),
        )
        row = cursor.fetchone()
        return row[0] if row and row[0] else None


def _get_all_spreadsheet_ids(column: str) -> list[str]:
    with conn() as connection:
        cursor = connection.cursor()
        cursor.execute(f'SELECT {column} FROM users')
        return [row[0] for row in cursor.fetchall() if row[0]]


def get_all_incomes_spreadsheet_ids() -> list[str]:
    return _get_all_spreadsheet_ids('incomes_spreadsheet_id')


def get_all_expenses_spreadsheet_ids() -> list[str]:
    return _get_all_spreadsheet_ids('expenses_spreadsheet_id')
