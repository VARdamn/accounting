from aiogram import executor
from aiogram import types
import schedule
import time
import datetime
import threading

import keyboards, handlers # DON'T REMOVE
from misc import dp, bot, months
from db import db
from google_sheets import google_sheets


def check_month():
    # if month has changed - creating new sheet
    if (datetime.date.today()-datetime.timedelta(days=1)).month + 1 == (datetime.date.today()).month:
        for spreadsheet_id in db.get_all_expenses_spreadsheet_ids():
            google_sheets.Expenses(spreadsheet_id).create_sheet()
        
        for spreadsheet_id in db.get_all_incomes_spreadsheet_ids():
            google_sheets.Incomes(spreadsheet_id).create_sheet()
                

def scheduler():
    schedule.every().day.at("01:00").do(check_month) 
    while True:
        schedule.run_pending()
        time.sleep(10)


async def set_commands(dispatcher):
    commands = [
        types.BotCommand(command="start", description="Start bot"),
        types.BotCommand(command="help", description="Get commands list with description"),
        types.BotCommand(command="add_expenses_spreadsheet", description="Добавить таблицу расходов"),
        types.BotCommand(command="add_incomes_spreadsheet", description="Добавить таблицу доходов"),
    ]
    await bot.set_my_commands(commands)


if __name__ == "__main__":
    db.init()
    check_month()
    threading.Thread(target=scheduler, daemon=True).start()
    executor.start_polling(dp, skip_updates=True, on_startup=set_commands)
