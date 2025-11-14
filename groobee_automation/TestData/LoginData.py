import openpyxl

class LoginData:

    #엑셀 데이터 받기
    @staticmethod
    def get_excel_data(data_num):
        path = openpyxl.load_workbook(r"/Users/ywj/Documents/PLATEER/automation/code/groobee-automation-project/GroobeeLoginData.xlsx")
        sheet = path.active
        result = {}

        for i in range(2, sheet.max_row + 1):
            if str(sheet.cell(row=i, column=1).value) == str(data_num):
                for j in range(2, sheet.max_column + 1):
                    key = sheet.cell(row=1, column=j).value
                    value = sheet.cell(row=i, column=j).value
                    result[key] = value
                break

        path.close()
        return [result]