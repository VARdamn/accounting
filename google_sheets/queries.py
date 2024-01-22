'''
This file contains body for different google sheets batch update requests
'''


def create_sheet__body(
        sheet_id: str, 
        values: list, 
        header_bg_color: dict, 
        action_bg_color: dict, 
        additional_header_bg_color: dict | None = None,
        additional_action_bg_color: dict | None = None
        ) -> dict:
    '''
    Returns body for create_sheet() function of Class Expenses.
    '''
    requests = [
            # creating table header
            {
                "updateCells": {
                    "fields": "*",
                    "rows": {
                        "values": values
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
                            "backgroundColor" : header_bg_color,
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
                            "backgroundColor" : action_bg_color,
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
                        "endColumnIndex": 5
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
                        "endColumnIndex": 7 if additional_header_bg_color else 5
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
    
    # this is expenses table
    if additional_header_bg_color:
        requests.append(# formatting size of columns накопительный счет
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
            }
        )

        requests.append(
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
                            "backgroundColor" : additional_header_bg_color,
                            "horizontalAlignment" : "CENTER",
                            "textFormat": {
                                "fontSize": 13,
                                "bold": True
                            }
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
                },
            }
        )

        requests.append(
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
                            "backgroundColor" : additional_action_bg_color,
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
            }
        )
    else:
        requests.append(
            # formatting size of column деятельность
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 1,
                        "endIndex": 2
                    },
                    "properties": {
                    "pixelSize": 
                        150
                    },
                    "fields": "pixelSize"
                }
            })
    return {
        "requests": requests
    }


def write_new_action__body(sheet_id: int, 
                           amount: float, 
                           category: str, 
                           date_of_transaction: str,
                           bg_color: dict, 
                           with_bottom: bool = False) -> dict:
    '''
    Returns body for write_new_action() function.
    '''
    return {
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
            # formatting all 4 cells
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 1,
                        "endRowIndex": 2,
                        "startColumnIndex": 0,
                        "endColumnIndex": 4
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "numberFormat" : {
                                "type": "CURRENCY",
                                "pattern": "#,##0.00[$₽-411]"
                            },
                            "backgroundColor" : bg_color,
                            "textFormat": {
                                "fontSize": 11
                            },
                            "horizontalAlignment": "CENTER"
                        }
                    },
                    "fields": "userEnteredFormat"
                }
            },
            {
                "updateBorders": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 1,
                        "endRowIndex": 1 if with_bottom else 3,
                        "startColumnIndex": 3,
                        "endColumnIndex": 4
                    },
                    "right": {
                        "style": "SOLID_MEDIUM"
                    },
                }
            },
            {
                "updateBorders": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 1,
                        "endRowIndex": 2,
                        "startColumnIndex": 0,
                        "endColumnIndex": 4
                    },
                    "bottom": None if not with_bottom else {"style": "SOLID_MEDIUM"}
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
        ]
    }


def get_chart_spec(sheet_id: int, transactions_count: int) -> dict:
    '''Returns spec for chart.'''
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
                            "endRowIndex": transactions_count,
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
                        "endRowIndex": transactions_count,
                        "startColumnIndex": 2,
                        "endColumnIndex": 3
                    }]
                }
            }
        }
    }


# def create_sheet_incomes__body(sheet_id: str) -> dict:
#     '''
#     Returns body for create_sheet() function for Incomes Class.
#     '''


# def write_new_action_incomes__body(sheet_id: str) -> dict:
#     '''
#     Returns body for write_new_action() function for Incomes Class.
#     '''

