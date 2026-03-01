from aiogram import Dispatcher

from handlers.commands import router as commands_router
from handlers.transactions import router as transactions_router


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.include_router(commands_router)
    dispatcher.include_router(transactions_router)
