from db import db
from google_sheets.google_sheets import Expenses, Incomes


def ensure_all_month_sheets_for_spreadsheet(spreadsheet_id: str, table_cls: type[Expenses] | type[Incomes]) -> None:
    if not spreadsheet_id:
        return
    table = table_cls(spreadsheet_id)
    table.ensure_all_month_sheets()


def ensure_all_user_month_sheets() -> None:
    for spreadsheet_id in db.get_all_expenses_spreadsheet_ids():
        ensure_all_month_sheets_for_spreadsheet(spreadsheet_id, Expenses)

    for spreadsheet_id in db.get_all_incomes_spreadsheet_ids():
        ensure_all_month_sheets_for_spreadsheet(spreadsheet_id, Incomes)
