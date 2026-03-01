from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from db import db
from google_sheets.google_sheets import Expenses, Incomes
from services.date_parser import parse_transaction_date

router = Router()


def _build_transaction_payload(raw_args: str) -> tuple[float, str, str]:
    args = raw_args.split()
    if len(args) not in (2, 3):
        raise ValueError('Использование: /команда <сумма> <категория> [дата]')

    try:
        amount = float(args[0])
    except ValueError as error:
        raise ValueError('Сумма должна быть числом') from error
    category = args[1]
    raw_date = args[2] if len(args) == 3 else None
    try:
        transaction_date = parse_transaction_date(raw_date).strftime('%d.%m.%Y')
    except ValueError as error:
        raise ValueError('Дата должна быть в формате дд, дд.мм или дд.мм.гггг') from error
    return amount, category, transaction_date


async def _handle_transaction_error(message: Message, error: Exception) -> None:
    if isinstance(error, ValueError):
        await message.answer(f'Ошибка: {error}')
        return
    await message.answer('Не удалось обработать команду')


def _extract_command_args(message_text: str) -> str:
    parts = message_text.split(maxsplit=1)
    return parts[1] if len(parts) == 2 else ''


@router.message(Command('трата'), F.chat.type == 'private')
async def cmd_expense(message: Message) -> None:
    try:
        amount, category, date_of_transaction = _build_transaction_payload(_extract_command_args(message.text))
    except Exception as error:
        await _handle_transaction_error(message, error)
        return

    spreadsheet_id = db.get_user_spreadsheet_id(str(message.chat.id), sheet_type='expenses')
    if not spreadsheet_id:
        await message.answer('Сначала добавьте таблицу расходов через /add_expenses_spreadsheet')
        return

    table = Expenses(spreadsheet_id, amount, category, date_of_transaction)
    if table.sheet_id is None:
        table.create_sheet()
    if table.get_transactions_count() < 1:
        table.with_bottom = True
        table.create_chart()
    else:
        table.update_chart()
    table.write_new_action()
    await message.answer('✅')


@router.message(Command('особая'), F.chat.type == 'private')
async def cmd_big_expense(message: Message) -> None:
    try:
        amount, category, date_of_transaction = _build_transaction_payload(_extract_command_args(message.text))
    except Exception as error:
        await _handle_transaction_error(message, error)
        return

    spreadsheet_id = db.get_user_spreadsheet_id(str(message.chat.id), sheet_type='expenses')
    if not spreadsheet_id:
        await message.answer('Сначала добавьте таблицу расходов через /add_expenses_spreadsheet')
        return

    table = Expenses(spreadsheet_id, amount, category, date_of_transaction, sheet_name='Особые траты')
    if table.sheet_id is None:
        table.create_sheet()
    table.write_new_action()
    await message.answer('✅')


@router.message(Command('доход'), F.chat.type == 'private')
async def cmd_income(message: Message) -> None:
    try:
        amount, category, date_of_transaction = _build_transaction_payload(_extract_command_args(message.text))
    except Exception as error:
        await _handle_transaction_error(message, error)
        return

    spreadsheet_id = db.get_user_spreadsheet_id(str(message.chat.id), sheet_type='incomes')
    if not spreadsheet_id:
        await message.answer('Сначала добавьте таблицу доходов через /add_incomes_spreadsheet')
        return

    table = Incomes(spreadsheet_id, amount, category, date_of_transaction)
    if table.sheet_id is None:
        table.create_sheet()
    if table.get_transactions_count() < 1:
        table.with_bottom = True
    table.write_new_action()
    await message.answer('✅')
