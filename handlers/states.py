from aiogram.dispatcher.filters.state import State, StatesGroup


class addExpensesSpreadsheet(StatesGroup):
    spreadsheet_id = State()


class addIncomesSpreadsheet(StatesGroup):
    spreadsheet_id = State()

