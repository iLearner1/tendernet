import xlrd
import os


def read_xls():

    dirname = os.path.dirname(__file__)
    files = ["Акмолинская область.xlsx",
             "Актюбинская область.xlsx",
             "Алматинская область.xlsx",
             "Атырауская область.xlsx",
             "Восточно-Казахстанская область.xlsx",
             "Жамбылская область.xlsx",
             "Западно-Казахстанская область.xlsx",
             "Карагандинская область.xlsx",
             "Костанайская область.xlsx",
             "Кызылординская область.xlsx",
             "Мангистауская область.xlsx",
             "область.xlsx",
             "Павлодарская область.xlsx",
             "Северо-Казахстанская область.xlsx",
             "Туркестанская область.xlsx"
             ]

    kato_list = {}
    for f in files:
        filename = dirname + "/kato_lists/"  + f

        # To open Workbook
        wb = xlrd.open_workbook(filename)
        sheet_0 = wb.sheet_by_index(0)

        for row in range(sheet_0.nrows):
            code = str(sheet_0.cell_value(row, 0))
            name = sheet_0.cell_value(row, 1)

            if code[2:] != "0000000":

                if '5532' in code or '3532' in code or '1942' in code or '5942' in code:
                    print("duplicate")
                else:
                    if not code in kato_list.keys():
                        kato_list[code[0:4] + "00000"] = name

    return kato_list