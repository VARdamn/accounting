from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db import db
from google_sheets.google_sheets import Expenses, Incomes
from handlers.states import AddExpensesSpreadsheetState, AddIncomesSpreadsheetState
from services.sheets_manager import ensure_all_month_sheets_for_spreadsheet

router = Router()


@router.message(CommandStart(), F.chat.type == 'private')
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer('This is simple bot. \nType /help to get all commands')


@router.message(Command('help'), F.chat.type == 'private')
async def cmd_help(message: Message, state: FSMContext) -> None:
    await state.clear()
    payload = 'разрабу пока лень сделать нормальный хелп, пните его по возможности - @yungyani_hayastan'
    await message.answer(payload)


@router.message(Command('add_expenses_spreadsheet'), F.chat.type == 'private')
async def cmd_add_expenses_sheet(message: Message, state: FSMContext) -> None:
    await message.answer('Введите ссылку на таблицу')
    await state.set_state(AddExpensesSpreadsheetState.spreadsheet_id)


@router.message(AddExpensesSpreadsheetState.spreadsheet_id, F.chat.type == 'private')
async def set_expenses_sheet(message: Message, state: FSMContext) -> None:
    spreadsheet_id = message.text.replace('https://docs.google.com/spreadsheets/d/', '')[:44]
    db.add_user_sheet(str(message.chat.id), spreadsheet_id, sheet_type='expenses')
    ensure_all_month_sheets_for_spreadsheet(spreadsheet_id, Expenses)
    await message.answer('Таблица расходов успешно добавлена! /help for info')
    await state.clear()


@router.message(Command('add_incomes_spreadsheet'), F.chat.type == 'private')
async def cmd_add_incomes_sheet(message: Message, state: FSMContext) -> None:
    await message.answer('Введите ссылку на таблицу')
    await state.set_state(AddIncomesSpreadsheetState.spreadsheet_id)


@router.message(AddIncomesSpreadsheetState.spreadsheet_id, F.chat.type == 'private')
async def set_incomes_sheet(message: Message, state: FSMContext) -> None:
    spreadsheet_id = message.text.replace('https://docs.google.com/spreadsheets/d/', '')[:44]
    db.add_user_sheet(str(message.chat.id), spreadsheet_id, sheet_type='incomes')
    ensure_all_month_sheets_for_spreadsheet(spreadsheet_id, Incomes)
    await message.answer('Таблица доходов успешно добавлена! /help for info')
    await state.clear()
