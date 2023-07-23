from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.filters import Text
from datetime import datetime, date

from google_sheets import google_sheets
from db import db
from misc import dp, bot, months


@dp.message_handler(commands=['start'], state="*", chat_type=types.ChatType.PRIVATE)
async def cmd_start(message: types.Message, state=None):
    await state.finish()
    await bot.send_message(message.chat.id, "This is simple bot. \nType /help to get all commands")


@dp.message_handler(commands=['test'], state="*", chat_type=types.ChatType.PRIVATE)
async def cmd_start(message: types.Message, state=None):
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


@dp.message_handler(commands=['add_sheet'], state="*", chat_type=types.ChatType.PRIVATE)
async def cmd_add_sheet(message: types.Message, state=None):
    args = message.get_args().split()
    spreadsheet_id = args[0].replace('https://docs.google.com/spreadsheets/d/', '')[:44]
    db.add_user_sheet(message.chat.id, spreadsheet_id)
    await bot.send_message(message.chat.id, "Table successfully added!")


@dp.message_handler(commands=['трата'], state="*", chat_type=types.ChatType.PRIVATE)
async def cmd_expense(message: types.Message, state=None):
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
    
    spreadsheet_id = db.get_user_spreadsheet_id(message.chat.id)
    # add new transaction to sheet
    if google_sheets.get_transactions_count(spreadsheet_id) < 1:
        google_sheets.write_new_action(spreadsheet_id, amount, category, date_of_transaction)
        print("creating chart")
        google_sheets.create_chart(spreadsheet_id)
    else:
        google_sheets.write_new_action(spreadsheet_id, amount, category, date_of_transaction)
        print("updating chart")
        google_sheets.update_chart(spreadsheet_id)
    await bot.send_message(message.chat.id, "✅")
