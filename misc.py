import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import dotenv_values

config = dict(dotenv_values(".env"))

bot = Bot(token=config['TOKEN'], parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)
