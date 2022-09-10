import asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.filters import Text

from db import db
from misc import dp, bot


@dp.message_handler(commands=['start'], state="*", chat_type=types.ChatType.PRIVATE)
async def cmd_start(message: types.Message, state=None):
    await state.finish()
    await bot.send_message(message.chat.id, "This is simple bot. \nType /help to get all commands")\


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
    db.add_user_sheet(message.chat.id, spreadsheet_id, args[1:])
    await bot.send_message(message.chat.id, "Table successfully added!")


@dp.message_handler(commands=['трата'], state="*", chat_type=types.ChatType.PRIVATE)
async def cmd_expense(message: types.Message, state=None):
    args = message.get_args().split()
    print(args, len((args)))