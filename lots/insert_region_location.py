import xlrd
import os


def read_xls():

    dirname = os.path.dirname(__file__)
    filename = dirname  + "/kato_list.xls"

    # To open Workbook
    wb = xlrd.open_workbook(filename)
    sheet_0 = wb.sheet_by_index(0)
    sheet_1 = wb.sheet_by_index(1)

    kato_list = {}

    for row in range(sheet_0.nrows):

        code = str(sheet_0.cell_value(row, 0))
        name = sheet_0.cell_value(row, 1)

        if not code in kato_list.keys():
            kato_list[code[0:4] + "00000"] = name

    for row in range(sheet_1.nrows):

        code = str(sheet_1.cell_value(row, 0))
        name = sheet_1.cell_value(row, 1)

        if not code in kato_list.keys():
            kato_list[code[0:4] + "00000"] = name

    return kato_list