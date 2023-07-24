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

spreadsheet_id = "1kuy63DWZbxY0GtsgNgsKlnfHFKE00G0G2WkZoHEjhpc"


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


def get_chart_spec(spreadsheet_id: str, sheet_id: int) -> dict:
    return {
        "title": "Диаграмма месячных расходов",
        "pieChart": {
            "legendPosition": "LABELED_LEGEND",
            "threeDimensional": True,
            "domain": {
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
                },
                "aggregateType": "SUM"
            },
            "series": {
                "sourceRange": {
                    "sources": [{
                        "sheetId": sheet_id,
                        "startRowIndex": 1,
                        "endRowIndex": get_transactions_count(spreadsheet_id)+2,
                        "startColumnIndex": 2,
                        "endColumnIndex": 3
                    }]
                },
                "aggregateType": "SUM"
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
                            # ячейка, которая будет левым верхним углом диаграммы
                            "overlayPosition": {
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


# create_chart(spreadsheet_id)
# update_chart(spreadsheet_id)

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
                # creating table header
                {
                    "updateCells": {
                        "fields": "*",
                        "rows": {
                            "values": [    
                                {"userEnteredValue": {"stringValue": "Дата"}}, 
                                {"userEnteredValue": {"stringValue": "Категория"}}, 
                                {"userEnteredValue": {"stringValue": "Сумма"}}, 
                                {"userEnteredValue": {"stringValue": "Примечания"}}, 
                                {"userEnteredValue": {"stringValue": "Всего за месяц"}}, 
                                {"userEnteredValue": {"stringValue": "Накопительный счет (начало месяца)"}},
                                {"userEnteredValue": {"stringValue": "Накопительный счет (конец месяца)"}}
                            ]
                        },
                        "start": {
                            "sheetId": sheet_id,
                            "rowIndex": 0,
                            "columnIndex": 0
                        }
                    }
                },
                # formula to calculate sum for month
                {
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
                            "columnIndex": 4
                        }
                    }
                },
                # formatting всего за месяц и накоп счет делаем рубли
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 1,
                            "endRowIndex": 2,
                            "startColumnIndex": 4,
                            "endColumnIndex": 7
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
                # formatting size of column примечания
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": 3,
                            "endIndex": 4
                        },
                        "properties": {
                        "pixelSize": 
                            135
                        },
                        "fields": "pixelSize"
                    }
                },
                # formatting size of column всего за месяц
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "COLUMNS",
                            "startIndex": 4,
                            "endIndex": 5
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
                            "startIndex": 5,
                            "endIndex": 7
                        },
                        "properties": {
                            "pixelSize": 
                                340
                            },
                        "fields": "pixelSize"
                    }
                },
                # formatting bg color накопительный счет header
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 5,
                            "endColumnIndex": 7
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor" : {
                                    "red": 0.58,
                                    "green": 0.77,
                                    "blue": 0.49
                                },
                                "horizontalAlignment" : "CENTER",
                                "textFormat": {
                                    "fontSize": 13,
                                    "bold": True
                                }
                            }
                        },
                        "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
                    },
                },
                # formatting bg color накопительный счет нижняя часть
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 1,
                            "endRowIndex": 2,
                            "startColumnIndex": 5,
                            "endColumnIndex": 7
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
                                    "pattern": "#,##0.00 [$₽-411]"
                                },
                                "horizontalAlignment" : "CENTER",
                                "textFormat": {
                                    "fontSize": 11
                                }
                            }
                        },
                        "fields": "userEnteredFormat(backgroundColor,numberFormat,textFormat,horizontalAlignment)"
                    }
                },
                # formatting bg color main header
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": 5
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor" : {
                                    "red": 0.96,
                                    "green": 0.7,
                                    "blue": 0.42
                                },
                                "horizontalAlignment" : "CENTER",
                                "textFormat": {
                                    "fontSize": 13,
                                    "bold": True
                                }
                            }
                        },
                        "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
                    }
                },
                # formatting bg color сумма всего за месяц
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 1,
                            "endRowIndex": 2,
                            "startColumnIndex": 4,
                            "endColumnIndex": 5
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor" : {
                                    "red": 1,
                                    "green": 0.95,
                                    "blue": 0.8
                                },
                                "horizontalAlignment" : "CENTER",
                                "textFormat": {
                                    "fontSize": 11
                                }
                            }
                        },
                        "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
                    }
                },

                #### ГРАНИЦЫ
                {
                    "updateBorders": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": 4
                        },
                        "bottom": {
                            "style": "SOLID_MEDIUM"
                        }
                    }
                },
                {
                    "updateBorders": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 0,
                            "endRowIndex": 2,
                            "startColumnIndex": 4,
                            "endColumnIndex": 7
                        },
                        "bottom": {
                            "style": "SOLID_MEDIUM"
                        },
                        "top": {
                            "style": "SOLID_MEDIUM"
                        },
                        "left": {
                            "style": "SOLID_MEDIUM"
                        },
                        "right": {
                            "style": "SOLID_MEDIUM"
                        },
                        "innerVertical": {
                            "style": "SOLID_MEDIUM"
                        },
                        "innerHorizontal": {
                            "style": "SOLID_MEDIUM"
                        }
                    }
                }
            ]
        }
    ).execute()


create_sheet(spreadsheet_id, "Август")


# print(31.95771+0.40316341+0.44267165+0.59100377+0.31019123+0.45588529+0.15698007+0.57640924+0.32817803+0.16970323+0.04578118+0.21970422+0.12991144+0.05595179+0.01047318+0.17150071+0.59207518+0.55458135+0.59544107)