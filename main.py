import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from db import db
from handlers import register_handlers
from services.scheduler import daily_sheets_maintenance_task
from services.sheets_manager import ensure_all_user_month_sheets


async def set_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command='start', description='Start bot'),
        BotCommand(command='help', description='Get commands list with description'),
        BotCommand(command='add_expenses_spreadsheet', description='Добавить таблицу расходов'),
        BotCommand(command='add_incomes_spreadsheet', description='Добавить таблицу доходов'),
    ]
    await bot.set_my_commands(commands)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=config['TOKEN'], default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dispatcher = Dispatcher(storage=MemoryStorage())
    register_handlers(dispatcher)

    db.init()
    ensure_all_user_month_sheets()
    asyncio.create_task(daily_sheets_maintenance_task())

    await set_commands(bot)
    await dispatcher.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
