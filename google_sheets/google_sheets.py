import httplib2
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime

from misc import months


CREDENTIALS_FILE = 'creds.json'

# Авторизуемся и получаем service — экземпляр доступа к API
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    CREDENTIALS_FILE,
    ['https://www.googleapis.com/auth/spreadsheets',
     'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = discovery.build('sheets', 'v4', http=httpAuth)


def create_sheet(spreadsheet_id: str, sheet_name: str):
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [
                {
                    # creating sheet
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }
            ]
        }
    ).execute()

    sheet_id = get_sheet_id_by_sheet_name(spreadsheet_id, sheet_name)

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [
                {
                    # creating table header
                    "updateCells": {
                        "fields": "*",
                        "rows": {
                            "values": [    
                                {"userEnteredValue": {"stringValue": "Дата"}}, 
                                {"userEnteredValue": {"stringValue": "Категория"}}, 
                                {"userEnteredValue": {"stringValue": "Сумма"}}, 
                                {"userEnteredValue": {"stringValue": "Примечания"}}, 
                                {"userEnteredValue": {"stringValue": ""}}, 
                                {"userEnteredValue": {"stringValue": "Всего за месяц"}}, 
                            ]
                        },
                        "start": {
                            "sheetId": sheet_id,
                            "rowIndex": 0,
                            "columnIndex": 0
                        }
                    }
                },
                {
                    # adding formula to calculate the amount for month
                    "updateCells": {
                        "fields": "*",
                        "rows": {
                            "values": [    
                                {"userEnteredValue": {"formulaValue": "=SUM(C:C)"}}, 
                            ]
                        },
                        "start": {
                            "sheetId": sheet_id,
                            "rowIndex": 1,
                            "columnIndex": 5
                        }
                    }
                },
                {
                    # formatting header; выравнивание по центру, шрифт 12 и жирный текст
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1
                        },
                        "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment" : "CENTER",
                            "textFormat": {
                            "fontSize": 11,
                            "bold": True
                            }
                        }
                        },
                        "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
                    }
                },
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": 5,
                            "endIndex": 6
                        },
                        "properties": {
                        "pixelSize": 
                            155
                        },
                        "fields": "pixelSize"
                    }
                },
            ]
        }
    ).execute()


def write_new_action(spreadsheet_id: str, amount: str, category: str, date_of_transaction: str) -> None:
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [
                # inserting empty rows
                {
                    "insertRange": {
                        "range": {
                            "sheetId": get_sheet_id_by_sheet_name(spreadsheet_id),
                            "startRowIndex": 1,
                            "endRowIndex": 2,
                            "startColumnIndex": 0,
                            "endColumnIndex": 4
                        },
                        "shiftDimension": "ROWS"
                    }
                },
                # inserting data
                {
                    "updateCells": {
                        "fields": "*",
                        "rows": {
                            "values": [    
                                {"userEnteredValue": {"stringValue": date_of_transaction}}, 
                                {"userEnteredValue": {"stringValue": category}}, 
                                {"userEnteredValue": {"stringValue": amount}}, 
                            ]
                        },
                        "start": {
                            "sheetId": get_sheet_id_by_sheet_name(spreadsheet_id),
                            "rowIndex": 1,
                            "columnIndex": 0
                        }
                    }
                },
                # sorting by date
                {
                    "sortRange": {
                        "range": {
                            "sheetId": get_sheet_id_by_sheet_name(spreadsheet_id),
                            "startRowIndex": 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": 4,
                        },
                        "sortSpecs": [
                            {
                                "dimensionIndex": 0,
                                "sortOrder": "DESCENDING"
                            }
                        ]
                    }
                }
            ]
        }
    ).execute()


def get_sheet_id_by_sheet_name(spreadsheet_id: str, sheet_name: str = None) -> str | None:
    name = sheet_name if sheet_name else months[datetime.now().month]
    sheets = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheets['sheets']
    for sheet in sheets:
        if sheet['properties']['title'] == name: # ex. months[datetime.now().month] == Сентябрь
            return sheet['properties']['sheetId']
    return None

