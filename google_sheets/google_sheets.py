import httplib2
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

from misc import months
import google_sheets.queries as q

CREDENTIALS_FILE = 'creds.json'
BASIC_DATE = datetime(1899, 12, 30)

credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = discovery.build('sheets', 'v4', http=httpAuth)


class Table:

    '''Basic table class.'''

    def __init__(self, 
                 spreadsheet_id: str, 
                 amount: float = 0, 
                 category: str = "CATEGORY", 
                 date_of_transaction: str = "01.01.1970",
                 sheet_name: str | None = None,  
                 with_bottom: bool = False
                ) -> None:
        self.spreadsheet_id = spreadsheet_id
        self.amount = amount
        self.category = category
        # self.date_of_transaction = date_of_transaction
        self.date_of_transaction = (datetime.strptime(date_of_transaction, '%d.%m.%Y') - BASIC_DATE).days
        self.sheet_name = sheet_name if sheet_name else months[datetime.now().month]
        self.with_bottom = with_bottom
        self.sheet_id = self.get_sheet_id_by_sheet_name()

    def get_sheet_id_by_sheet_name(self) -> int | None:
        sheets = service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
        sheets = sheets['sheets']
        for sheet in sheets:
            if sheet['properties']['title'] == self.sheet_name: # ex. months[datetime.now().month] == Сентябрь
                return sheet['properties']['sheetId']
        return None

    def get_transactions_count(self) -> int:
        arr = service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{months[datetime.now().month]}!B1:B"
        ).execute().get("values")
        return len(arr)-1

    def get_all_categories(self) -> list:
        arr = service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id,
            range=f"{months[datetime.now().month]}!B1:B"
        ).execute().get("values")

        return list(set([el[0] for el in arr]))


class Expenses(Table):

    '''
    Class for Expenses table.
    '''
    
    def __init__(self, 
                 spreadsheet_id: str, 
                 amount: float = 0, 
                 category: str = "CATEGORY", 
                 date_of_transaction: str = "01.01.1970",
                 sheet_name: str | None = None,  
                 with_bottom: bool = False
                ) -> None:
        super().__init__(spreadsheet_id, amount, category, date_of_transaction, sheet_name, with_bottom)
        self.header_bg_color = {
            "red": 0.96,
            "green": 0.7,
            "blue": 0.42
        }
        self.action_bg_color = {
            "red": 1,
            "green": 0.95,
            "blue": 0.8
        }
        self.additional_header_bg_color = {
            "red": 224/255,
            "green": 102/255,
            "blue": 102/255
        }
        self.additional_action_bg_color = {
            "red": 234/255,
            "green": 153/255,
            "blue": 153/255
        }

    def create_sheet(self):
        service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={
                "requests": [{
                    # creating sheet
                    'addSheet': {
                        'properties': {
                            'title': self.sheet_name
                        }
                    }
                }]
            }
        ).execute()

        service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=q.create_sheet__body(self.get_sheet_id_by_sheet_name(), [    
                            {"userEnteredValue": {"stringValue": "Дата"}}, 
                            {"userEnteredValue": {"stringValue": "Категория"}}, 
                            {"userEnteredValue": {"stringValue": "Сумма"}}, 
                            {"userEnteredValue": {"stringValue": "Примечания"}}, 
                            {"userEnteredValue": {"stringValue": "Всего за месяц"}}, 
                            {"userEnteredValue": {"stringValue": "Накопительный счет (начало месяца)"}},
                            {"userEnteredValue": {"stringValue": "Накопительный счет (конец месяца)"}}
                        ], self.header_bg_color, self.action_bg_color, self.additional_header_bg_color, self.additional_action_bg_color)
        ).execute()

    def write_new_action(self) -> None:
        service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=q.write_new_action__body(self.sheet_id, self.amount, self.category, self.date_of_transaction, self.action_bg_color, self.with_bottom)
        ).execute()

    def get_chart_id(self) -> int:
        arr = service.spreadsheets().get(
            spreadsheetId=self.spreadsheet_id,
            ranges=[f"{months[datetime.now().month]}!A1:Z100"]
            # ranges=[f"Декабрь!A1:Z100"]
        ).execute()
        return arr.get("sheets")[0].get("charts")[0].get("chartId")

    def create_chart(self):
        service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={
                "requests": [{
                    "addChart": {
                        "chart": {
                            "spec": q.get_chart_spec(self.sheet_id, self.get_transactions_count()+2),
                            "position": {
                                "overlayPosition": {
                                    # ячейка, которая будет левым верхним углом диаграммы
                                    "anchorCell": {
                                        "sheetId": self.sheet_id,
                                        "rowIndex": 10,
                                        "columnIndex": 5
                                    }
                                }
                            }
                        }
                    }
                }]
            }
        ).execute()

    def update_chart(self):
        service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={
                "requests": [{
                    "updateChartSpec": {
                        "chartId": self.get_chart_id(),
                        "spec": q.get_chart_spec(self.sheet_id, self.get_transactions_count()+2)
                }
                }]
            }
        ).execute()

    
class Incomes(Table):
    
    '''
    Class for Incomes table.
    '''

    def __init__(self, 
                 spreadsheet_id: str, 
                 amount: float = 0, 
                 category: str = "CATEGORY", 
                 date_of_transaction: str = "01.01.1970",
                 sheet_name: str | None = None,  
                 with_bottom: bool = False
                ) -> None:
        super().__init__(spreadsheet_id, amount, category, date_of_transaction, sheet_name, with_bottom)
        self.header_bg_color = {
            "red": 0.58,
            "green": 0.77,
            "blue": 0.49
        }
        self.action_bg_color = {
            "red": 0.85,
            "green": 0.92,
            "blue": 0.83
        }

    def create_sheet(self):
        service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={
                "requests": [{
                    # creating sheet
                    'addSheet': {
                        'properties': {
                            'title': self.sheet_name
                        }
                    }
                }]
            }
        ).execute()

        service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=q.create_sheet__body(self.get_sheet_id_by_sheet_name(), [    
                            {"userEnteredValue": {"stringValue": "Дата"}}, 
                            {"userEnteredValue": {"stringValue": "Деятельность"}}, 
                            {"userEnteredValue": {"stringValue": "Сумма"}}, 
                            {"userEnteredValue": {"stringValue": "Примечания"}}, 
                            {"userEnteredValue": {"stringValue": "Общий доход"}} 
                        ], self.header_bg_color, self.action_bg_color, None)
        ).execute()


    def write_new_action(self) -> None:
        service.spreadsheets().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=q.write_new_action__body(self.sheet_id, self.amount, self.category, self.date_of_transaction, self.action_bg_color, self.with_bottom)
        ).execute()
