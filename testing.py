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


create_chart(spreadsheet_id)
update_chart(spreadsheet_id)
