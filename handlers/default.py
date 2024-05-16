from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.filters import Text
from datetime import datetime, date

from . import states as st
from google_sheets import google_sheets
from db import db
from misc import dp, bot, months


@dp.message_handler(commands=['start'], state="*", chat_type=types.ChatType.PRIVATE)
async def cmd_start(message: types.Message, state=None):
    await state.finish()
    await bot.send_message(message.chat.id, "This is simple bot. \nType /help to get all commands")


@dp.message_handler(commands=['test'], state="*", chat_type=types.ChatType.PRIVATE)
async def cmd_test(message: types.Message, state=None):
    await state.finish()
    spreadsheet_id = db.get_user_spreadsheet_id(message.chat.id)
    google_sheets.get_all_categories(spreadsheet_id)
    

@dp.message_handler(commands=['help'], state="*", chat_type=types.ChatType.PRIVATE)
async def cmd_help(message: types.Message, state=None):
    await state.finish()
    payload = '''
        разрабу пока лень сделать нормальный хелп, пните его по возможности - @yungyani_hayastan 
    ''' #TODO: all commands list + description
    await bot.send_message(message.chat.id, payload)


@dp.message_handler(commands=['add_expenses_spreadsheet'], state="*", chat_type=types.ChatType.PRIVATE)
async def cmd_add_expenses_sheet(message: types.Message, state=None):
    await bot.send_message(message.chat.id, "Введите ссылку на таблицу")
    await st.addExpensesSpreadsheet.spreadsheet_id.set()

@dp.message_handler(state=st.addExpensesSpreadsheet.spreadsheet_id, chat_type=types.ChatType.PRIVATE)
async def cmd_add_expenses_sheet(message: types.Message, state: FSMContext):
    spreadsheet_id = message.text.replace('https://docs.google.com/spreadsheets/d/', '')[:44]
    db.add_user_sheet(message.chat.id, spreadsheet_id, _type='expenses')
    await bot.send_message(message.chat.id, "Таблица расходов успешно добавлена! /help for info")
    await state.finish()


@dp.message_handler(commands=['add_incomes_spreadsheet'], state="*", chat_type=types.ChatType.PRIVATE)
async def cmd_add_imcomes_sheet(message: types.Message, state=None):
    await bot.send_message(message.chat.id, "Введите ссылку на таблицу")
    await st.addIncomesSpreadsheet.spreadsheet_id.set()

@dp.message_handler(state=st.addIncomesSpreadsheet.spreadsheet_id, chat_type=types.ChatType.PRIVATE)
async def cmd_add_incomes_sheet(message: types.Message, state: FSMContext):
    spreadsheet_id = message.text.replace('https://docs.google.com/spreadsheets/d/', '')[:44]
    db.add_user_sheet(message.chat.id, spreadsheet_id, _type='incomes')
    await bot.send_message(message.chat.id, "Таблица доходов успешно добавлена! /help for info")
    await state.finish()


@dp.message_handler(commands=['трата'], state="*", chat_type=types.ChatType.PRIVATE)
async def cmd_expense(message: types.Message, state=None):
    args = message.get_args().split()
    # defining amount, category and date of transaction

    # got only amount and category --> date is today
    if len(args) == 2: 
        amount, category = args
        date_of_transaction = (date.today()).strftime("%d.%m.%Y")
    elif len(args) == 3:
        amount, category, date_of_transaction = args
        date_data = date_of_transaction.split('.')
        # if specified only day or day and month
        date_of_transaction = datetime(datetime.now().year, datetime.now().month, int(date_of_transaction)).strftime("%d.%m.%Y") \
            if len(date_data) == 1 else \
            datetime(datetime.now().year, int(date_data[1]), int(date_data[0])).strftime("%d.%m.%Y")
    
    spreadsheet_id = db.get_user_spreadsheet_id(message.chat.id, _type="expenses")
    table = google_sheets.Expenses(spreadsheet_id, float(amount), category, date_of_transaction)
    # add first transaction to sheet
    if table.get_transactions_count() < 1:
        table.with_bottom = True
        table.create_chart()
    else:
        table.update_chart()
    table.write_new_action()
    await bot.send_message(message.chat.id, "✅")


@dp.message_handler(commands=['крупная'], state="*", chat_type=types.ChatType.PRIVATE)
async def cmd_big_expense(message: types.Message, state=None):
    args = message.get_args().split()

    if len(args) == 2: 
        amount, category = args
        date_of_transaction = (date.today()).strftime("%d.%m.%Y")
    elif len(args) == 3:
        amount, category, date_of_transaction = args
        date_data = date_of_transaction.split('.')
        # if specified only day or day and month
        date_of_transaction = datetime(datetime.now().year, datetime.now().month, int(date_of_transaction)).strftime("%d.%m.%Y") \
            if len(date_data) == 1 else \
            datetime(datetime.now().year, int(date_data[1]), int(date_data[0])).strftime("%d.%m.%Y")
    
    spreadsheet_id = db.get_user_spreadsheet_id(message.chat.id, _type="expenses")
    table = google_sheets.Expenses(spreadsheet_id, float(amount), category, date_of_transaction, sheet_name='Крупные траты')
    table.write_new_action()
    await bot.send_message(message.chat.id, "✅")


@dp.message_handler(commands=['доход'], state="*", chat_type=types.ChatType.PRIVATE)
async def cmd_income(message: types.Message, state=None):
    args = message.get_args().split()
    # defining amount, category and date of transaction
    if len(args) == 2: # got only amount and category --> date is today
        amount, category = args
        date_of_transaction = (date.today()).strftime("%d.%m.%Y")
    elif len(args) == 3:
        amount, category, date_of_transaction = args
        date_data = date_of_transaction.split('.')
        # if specified only day or day and month
        date_of_transaction = datetime(datetime.now().year, datetime.now().month, int(date_of_transaction)).strftime("%d.%m.%Y") \
            if len(date_data) == 1 else \
            datetime(datetime.now().year, int(date_data[1]), int(date_data[0])).strftime("%d.%m.%Y")
    
    spreadsheet_id = db.get_user_spreadsheet_id(message.chat.id, _type="incomes")
    table = google_sheets.Incomes(spreadsheet_id, float(amount), category, date_of_transaction)
    # add first transaction to sheet
    if table.get_transactions_count() < 1:
        table.with_bottom = True
    table.write_new_action()
    await bot.send_message(message.chat.id, "✅")
