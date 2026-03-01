from aiogram.fsm.state import State, StatesGroup


class AddExpensesSpreadsheetState(StatesGroup):
    spreadsheet_id = State()


class AddIncomesSpreadsheetState(StatesGroup):
    spreadsheet_id = State()
