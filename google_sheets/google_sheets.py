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
                                {"userEnteredValue": {"stringValue": ""}}, 
                                {"userEnteredValue": {"stringValue": "Накопительный счет на начало месяца"}},
                                {"userEnteredValue": {"stringValue": "Накопительный счет на конец месяца"}}
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
                                {"userEnteredValue": {"formulaValue": "=SUM(C:C)"}}
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
                    # formatting общая сумма за месяц
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 1,
                            "endRowIndex": 2,
                            "startColumnIndex": 5,
                            "endColumnIndex": 9
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "numberFormat" : {
                                    "type": "CURRENCY",
                                    "pattern": "#,##0.00[$₽-411]"
                                },
                                "horizontalAlignment" : "CENTER",                                
                            }
                        },
                        "fields": "userEnteredFormat(numberFormat,horizontalAlignment)"
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
                # formatting size of column
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
                            150
                        },
                        "fields": "pixelSize"
                    }
                },
                # formatting size of columns накопительный счет
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": 7,
                            "endIndex": 9
                        },
                        "properties": {
                            "pixelSize": 
                                305
                            },
                        "fields": "pixelSize"
                    }
                },
                {
                    # formatting bg накопительный счет
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 7,
                            "endColumnIndex": 9
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor" : {
                                    "red": 0.85,
                                    "green": 0.92,
                                    "blue": 0.83
                                },
                                "numberFormat" : {
                                    "type": "CURRENCY",
                                    "pattern": "#,##0.00[$₽-411]"
                                }
                            }
                        },
                        "fields": "userEnteredFormat(backgroundColor,numberFormat)"
                    }
                }
            ]
        }
    ).execute()


def write_new_action(spreadsheet_id: str, amount: str, category: str, date_of_transaction: str) -> None:
    sheet_id = get_sheet_id_by_sheet_name(spreadsheet_id)
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [
                # inserting empty rows
                {
                    "insertRange": {
                        "range": {
                            "sheetId": sheet_id,
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
                                {"userEnteredValue": {"numberValue": float(amount)}}, 
                            ]
                        },
                        "start": {
                            "sheetId": sheet_id,
                            "rowIndex": 1,
                            "columnIndex": 0
                        }
                    }
                },
                # sorting by date
                {
                    "sortRange": {
                        "range": {
                            "sheetId": sheet_id,
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
                },
                # formatting 
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 1,
                            "endRowIndex": 2,
                            "startColumnIndex": 2,
                            "endColumnIndex": 3
                        },
                        "cell": {
                        "userEnteredFormat": {
                            "horizontalAlignment" : "CENTER",
                            "numberFormat" : {
                                "type": "CURRENCY",
                                "pattern": "#,##0.00[$₽-411]"
                            },
                            "textFormat": {
                            }
                        }
                        },
                        "fields": "userEnteredFormat(numberFormat,textFormat,horizontalAlignment)"
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


def get_transactions_count(spreadsheet_id: str) -> int:
    arr = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{months[datetime.now().month]}!B1:B"
    ).execute().get("values")
    return len(arr)-1


def get_all_categories(spreadsheet_id: str) -> list:
    arr = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=f"{months[datetime.now().month]}!B1:B"
    ).execute().get("values")

    return list(set([el[0] for el in arr]))


def get_chart_spec(spreadsheet_id: str, sheet_id: int) -> dict:
    return {
        "title": "Диаграмма месячных расходов",
        "pieChart": {
            "legendPosition": "LABELED_LEGEND",
            "threeDimensional": True,
            "domain": {
                "aggregateType": "SUM",
                "sourceRange": {
                    "sources": [
                        {
                            "sheetId": sheet_id,
                            "startRowIndex": 1,
                            "endRowIndex": get_transactions_count(spreadsheet_id)+2,
                            "startColumnIndex": 1,
                            "endColumnIndex": 2
                        }
                    ]
                }
            },
            "series": {
                "aggregateType": "SUM",
                "sourceRange": {
                    "sources": [{
                        "sheetId": sheet_id,
                        "startRowIndex": 1,
                        "endRowIndex": get_transactions_count(spreadsheet_id)+2,
                        "startColumnIndex": 2,
                        "endColumnIndex": 3
                    }]
                }
            }
        }
    }


def get_chart_id(spreadsheet_id: str) -> int:
    arr = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        ranges=[f"{months[datetime.now().month]}!A1:Z100"]
    ).execute()
    return arr.get("sheets")[0].get("charts")[0].get("chartId")


def create_chart(spreadsheet_id: str):
    sheet_id = get_sheet_id_by_sheet_name(spreadsheet_id=spreadsheet_id)
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [{
                "addChart": {
                    "chart": {
                        "spec": get_chart_spec(spreadsheet_id, sheet_id),
                        "position": {
                            "overlayPosition": {
                                # ячейка, которая будет левым верхним углом диаграммы
                                "anchorCell": {
                                    "sheetId": sheet_id,
                                    "rowIndex": 10,
                                    "columnIndex": 6
                                }
                            }
                        }
                    }
                }
            }]
        }
    ).execute()


def update_chart(spreadsheet_id: str):
    sheet_id = get_sheet_id_by_sheet_name(spreadsheet_id=spreadsheet_id)
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "requests": [{
                "updateChartSpec": {
                    "chartId": get_chart_id(spreadsheet_id),
                    "spec": get_chart_spec(spreadsheet_id, sheet_id)
                }
            }]
        }
    ).execute()

    