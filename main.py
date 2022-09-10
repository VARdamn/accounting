from aiogram import executor
from aiogram import types

import keyboards, handlers # DON'T REMOVE
from misc import dp, bot
from db import db

async def set_commands(dispatcher):
    commands = [
        types.BotCommand(command="start", description="Start bot"),
        types.BotCommand(command="help", description="Get commands list with description"),
    ]
    await bot.set_my_commands(commands)


if __name__ == "__main__":
    db.init()
    executor.start_polling(dp, skip_updates=True, on_startup=set_commands)
