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
        for spreadsheet_id in db.get_all_users_spreadsheet_ids():
            google_sheets.create_sheet(spreadsheet_id, months[(datetime.date.today()).month])


def scheduler():
    schedule.every().day.at("01:00").do(check_month) 
    while True:
        schedule.run_pending()
        time.sleep(10)


async def set_commands(dispatcher):
    commands = [
        types.BotCommand(command="start", description="Start bot"),
        types.BotCommand(command="help", description="Get commands list with description"),
    ]
    await bot.set_my_commands(commands)


if __name__ == "__main__":
    db.init()
    threading.Thread(target=scheduler, daemon=True).start()
    executor.start_polling(dp, skip_updates=True, on_startup=set_commands)
