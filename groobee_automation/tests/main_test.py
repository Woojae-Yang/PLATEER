

import os
import pytest
import time
from datetime import datetime

from PageObjects.LoginPage import LoginPage
from PageObjects.segment import SegmentPage
from TestData.LoginData import LoginData
from tests.test_groobeeLogin import TestDashboard
from utilities.BaseClass import BaseClass

#엑셀 데이터 불러오기
@pytest.fixture(params=LoginData.get_excel_data("1"))
def get_data(request):
    return request.param

def main():
    now = datetime.now()
    now_date = now.strftime('%Y.%m.%d')
    now_time = now.strftime('%H:%M:%S')

    tst = TestDashboard(driver)
    seg_page = SegmentPage(driver)

    tst.test_login(get_data)
    time.sleep(3)
    seg_page.create_segment(now_date)


#%%
if __name__ == "__main__":
    main()
    


