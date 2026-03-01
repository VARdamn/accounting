from datetime import datetime

import httplib2
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

import google_sheets.queries as q
from config import MONTHS

CREDENTIALS_FILE = 'creds.json'
BASIC_DATE = datetime(1899, 12, 30)

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'],
)
http_auth = credentials.authorize(httplib2.Http())
service = discovery.build('sheets', 'v4', http=http_auth)


class Table:
    _sheet_map_cache: dict[str, dict[str, int]] = {}

    def __init__(
        self,
        spreadsheet_id: str,
        amount: float = 0,
        category: str = 'CATEGORY',
        date_of_transaction: str | None = None,
        sheet_name: str | None = None,
        with_bottom: bool = False,
    ) -> None:
        self.spreadsheet_id = spreadsheet_id
        self.amount = amount
        self.category = category
        self.transaction_datetime = (
            datetime.strptime(date_of_transaction, '%d.%m.%Y')
            if date_of_transaction
            else datetime.now()
        )
        self.date_of_transaction = (self.transaction_datetime - BASIC_DATE).days
        self.sheet_name = sheet_name or MONTHS[self.transaction_datetime.month]
        self.with_bottom = with_bottom
        self.sheet_id = self.get_sheet_id_by_sheet_name(self.sheet_name)

    def _load_sheet_map(self, force: bool = False) -> dict[str, int]:
        if not force and self.spreadsheet_id in self._sheet_map_cache:
            return self._sheet_map_cache[self.spreadsheet_id]

        spreadsheet = service.spreadsheets().get(
            spreadsheetId=self.spreadsheet_id,
            fields='sheets(properties(sheetId,title))',
        ).execute()
        sheet_map = {
            sheet['properties']['title']: sheet['properties']['sheetId']
            for sheet in spreadsheet.get('sheets', [])
        }
        self._sheet_map_cache[self.spreadsheet_id] = sheet_map
        return sheet_map

    def _cache_sheet(self, title: str, sheet_id: int) -> None:
        sheet_map = self._load_sheet_map()
        sheet_map[title] = sheet_id

    def _add_sheets(self, sheet_names: list[str]) -> list[tuple[str, int]]:
        if not sheet_names:
            return []

        response = service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={
                'requests': [
                    {
                        'addSheet': {
                            'properties': {
                                'title': name,
                            }
                        }
                    }
                    for name in sheet_names
                ]
            },
        ).execute()

        created_sheets: list[tuple[str, int]] = []
        replies = response.get('replies', [])
        for name, reply in zip(sheet_names, replies):
            sheet_id = reply['addSheet']['properties']['sheetId']
            self._cache_sheet(name, sheet_id)
            created_sheets.append((name, sheet_id))
        return created_sheets

    def _build_create_sheet_requests(self, sheet_id: int) -> list[dict]:
        raise NotImplementedError

    def _format_new_sheets(self, sheet_ids: list[int]) -> None:
        if not sheet_ids:
            return

        requests: list[dict] = []
        for sheet_id in sheet_ids:
            requests.extend(self._build_create_sheet_requests(sheet_id))

        if requests:
            service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': requests},
            ).execute()

    def create_sheet(self, sheet_name: str | None = None) -> None:
        target_sheet_name = sheet_name or self.sheet_name
        existing_sheet_id = self.get_sheet_id_by_sheet_name(target_sheet_name)
        if existing_sheet_id is not None:
            if target_sheet_name == self.sheet_name:
                self.sheet_id = existing_sheet_id
            return

        created = self._add_sheets([target_sheet_name])
        if not created:
            return

        created_sheet_id = created[0][1]
        self._format_new_sheets([created_sheet_id])

        if target_sheet_name == self.sheet_name:
            self.sheet_id = created_sheet_id

    def ensure_all_month_sheets(self) -> None:
        sheet_map = self._load_sheet_map()
        missing_months = [month_name for month_name in MONTHS.values() if month_name not in sheet_map]
        created_sheets = self._add_sheets(missing_months)
        self._format_new_sheets([sheet_id for _, sheet_id in created_sheets])

    def get_sheet_titles(self) -> list[str]:
        return list(self._load_sheet_map().keys())

    def get_sheet_id_by_sheet_name(self, sheet_name: str | None = None) -> int | None:
        target_sheet_name = sheet_name or self.sheet_name
        return self._load_sheet_map().get(target_sheet_name)

    def get_transactions_count(self) -> int:
        arr = service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f'{self.sheet_name}!B1:B',
        ).execute().get('values', [])
        return max(len(arr) - 1, 0)

    def get_all_categories(self) -> list[str]:
        arr = service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f'{self.sheet_name}!B1:B',
        ).execute().get('values', [])
        return list(set(el[0] for el in arr if el))


class Expenses(Table):
    def __init__(
        self,
        spreadsheet_id: str,
        amount: float = 0,
        category: str = 'CATEGORY',
        date_of_transaction: str | None = None,
        sheet_name: str | None = None,
        with_bottom: bool = False,
    ) -> None:
        super().__init__(spreadsheet_id, amount, category, date_of_transaction, sheet_name, with_bottom)
        self.header_bg_color = {
            'red': 0.96,
            'green': 0.7,
            'blue': 0.42,
        }
        self.action_bg_color = {
            'red': 1,
            'green': 0.95,
            'blue': 0.8,
        }
        self.additional_header_bg_color = {
            'red': 224 / 255,
            'green': 102 / 255,
            'blue': 102 / 255,
        }
        self.additional_action_bg_color = {
            'red': 234 / 255,
            'green': 153 / 255,
            'blue': 153 / 255,
        }

    def _build_create_sheet_requests(self, sheet_id: int) -> list[dict]:
        return q.create_sheet__body(
            sheet_id,
            [
                {'userEnteredValue': {'stringValue': 'Дата'}},
                {'userEnteredValue': {'stringValue': 'Категория'}},
                {'userEnteredValue': {'stringValue': 'Сумма'}},
                {'userEnteredValue': {'stringValue': 'Примечания'}},
                {'userEnteredValue': {'stringValue': 'Всего за месяц'}},
                {'userEnteredValue': {'stringValue': 'Накопительный счет (начало месяца)'}},
                {'userEnteredValue': {'stringValue': 'Накопительный счет (конец месяца)'}},
            ],
            self.header_bg_color,
            self.action_bg_color,
            self.additional_header_bg_color,
            self.additional_action_bg_color,
        )['requests']

    def write_new_action(self) -> None:
        if self.sheet_id is None:
            self.create_sheet()
        service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=q.write_new_action__body(
                self.sheet_id,
                self.amount,
                self.category,
                self.date_of_transaction,
                self.action_bg_color,
                self.with_bottom,
            ),
        ).execute()

    def get_chart_id(self) -> int | None:
        arr = service.spreadsheets().get(
            spreadsheetId=self.spreadsheet_id,
            fields='sheets(properties(sheetId),charts(chartId))',
        ).execute()
        for sheet in arr.get('sheets', []):
            if sheet.get('properties', {}).get('sheetId') != self.sheet_id:
                continue
            charts = sheet.get('charts', [])
            return charts[0].get('chartId') if charts else None
        return None

    def create_chart(self) -> None:
        service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={
                'requests': [{
                    'addChart': {
                        'chart': {
                            'spec': q.get_chart_spec(self.sheet_id, self.get_transactions_count() + 1),
                            'position': {
                                'overlayPosition': {
                                    'anchorCell': {
                                        'sheetId': self.sheet_id,
                                        'rowIndex': 10,
                                        'columnIndex': 5,
                                    }
                                }
                            },
                        }
                    }
                }]
            },
        ).execute()

    def update_chart(self) -> None:
        chart_id = self.get_chart_id()
        if chart_id is None:
            self.create_chart()
            return
        service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={
                'requests': [{
                    'updateChartSpec': {
                        'chartId': chart_id,
                        'spec': q.get_chart_spec(self.sheet_id, self.get_transactions_count() + 1),
                    }
                }]
            },
        ).execute()


class Incomes(Table):
    def __init__(
        self,
        spreadsheet_id: str,
        amount: float = 0,
        category: str = 'CATEGORY',
        date_of_transaction: str | None = None,
        sheet_name: str | None = None,
        with_bottom: bool = False,
    ) -> None:
        super().__init__(spreadsheet_id, amount, category, date_of_transaction, sheet_name, with_bottom)
        self.header_bg_color = {
            'red': 0.58,
            'green': 0.77,
            'blue': 0.49,
        }
        self.action_bg_color = {
            'red': 0.85,
            'green': 0.92,
            'blue': 0.83,
        }

    def _build_create_sheet_requests(self, sheet_id: int) -> list[dict]:
        return q.create_sheet__body(
            sheet_id,
            [
                {'userEnteredValue': {'stringValue': 'Дата'}},
                {'userEnteredValue': {'stringValue': 'Деятельность'}},
                {'userEnteredValue': {'stringValue': 'Сумма'}},
                {'userEnteredValue': {'stringValue': 'Примечания'}},
                {'userEnteredValue': {'stringValue': 'Общий доход'}},
            ],
            self.header_bg_color,
            self.action_bg_color,
            None,
        )['requests']

    def write_new_action(self) -> None:
        if self.sheet_id is None:
            self.create_sheet()
        service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=q.write_new_action__body(
                self.sheet_id,
                self.amount,
                self.category,
                self.date_of_transaction,
                self.action_bg_color,
                self.with_bottom,
            ),
        ).execute()
