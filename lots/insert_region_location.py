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
    dup = 0
    non_dup = 0
    for f in files:
        filename = dirname + "/kato_lists/"  + f
        print("filename: ", filename)

        # To open Workbook
        wb = xlrd.open_workbook(filename)
        sheet_0 = wb.sheet_by_index(0)

        for row in range(sheet_0.nrows):

            code = str(sheet_0.cell_value(row, 0))
            name = sheet_0.cell_value(row, 1)

            print("code.type: ", type(code))
            if code == "155200000":
                print('code == "155200000":')
            if code[2:] != "0000000":
                if code == "553200000":
                    print("dupm code: ", code)
                    dup += 1
                elif code == "353200000":
                    print("dupm code: ", code)
                    dup += 1
                elif code == "194200000":
                    print("dupm code: ", code)
                    dup += 1
                elif code == "594200000":
                    print("dupm code: ", code)
                    print("the duplicate code: ", code)
                    dup += 1
                else:
                    print("not in duplicate")
                    non_dup += 1
                    if not code in kato_list.keys():
                        kato_list[code[0:4] + "00000"] = name

    print("dup: ", dup)
    print("non_dup: ", non_dup)
    return kato_list