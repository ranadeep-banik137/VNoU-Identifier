import json
import xlsxwriter
from modules.database import fetch_table_data
import pandas


def export_db_to_excel(table_name):

    # Create an new Excel file and add a worksheet.
    workbook = xlsxwriter.Workbook(table_name + '.xlsx')
    worksheet = workbook.add_worksheet('DEFAULT')

    # Create style for cells
    header_cell_format = workbook.add_format({'bold': True, 'border': True, 'bg_color': 'yellow'})
    body_cell_format = workbook.add_format({'border': True})

    header, rows = fetch_table_data(table_name)

    row_index = 0
    column_index = 0

    for column_name in header:
        worksheet.write(row_index, column_index, column_name, header_cell_format)
        column_index += 1

    row_index += 1
    for row in rows:
        column_index = 0
        for column in row:
            if column_index == 2:
                column = column.decode('ISO-8859-1')
            worksheet.write(row_index, column_index, column, body_cell_format)
            column_index += 1
        row_index += 1

    print(str(row_index) + ' rows written successfully to ' + workbook.filename)
    # Closing workbook
    workbook.close()


def export_excel_to_json(workbook_location, sheet_name='DEFAULT'):
    excel_data_fragment = pandas.read_excel(workbook_location, sheet_name=sheet_name)
    json_str = excel_data_fragment.to_json(orient="records")
    print('Excel Sheet to JSON:\n', json_str)
    return json.loads(json_str)


def export_db_to_json(table_name):
    data = []
    header, rows = fetch_table_data(table_name)
    header_list = []

    for head in header:
        header_list.append(head)

    for row in rows:
        value_list = []
        for column in row:
            value_list.append(column)
        mapper = {header[0]: value_list[0], header[1]: value_list[1], header[2]: value_list[2].decode('ISO-8859-1')}
        data.append(mapper)
    return json.dumps(data)
