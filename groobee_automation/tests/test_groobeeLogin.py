import time
import pytest
import sys 
import os 
from PageObjects.LoginPage import loginpage
from TestData.LoginData import LoginData
from utilities.BaseClass import BaseClass

#엑셀 데이터 불러오기
@pytest.fixture(params=LoginData.get_excel_data("1"))
def get_data(request):
    return request.param

class TestDashboard(BaseClass):

    login_expect_title = "대시보드 :: GROOBEE"

    def test_login(self, get_data):
        log = self.get_log()

        groobee = Dashboard(self.driver)

        #ID/PW 입력
        groobee.send_id().send_keys(get_data["ID"])
        groobee.send_pw().send_keys(get_data["PW"])

        time.sleep(1)

        #로그인 시도
        groobee.click_login_btn()
        
        #고객사 검색
        groobee.search_shop()

        time.sleep(1)

        #대시보드 진입
        groobee.click_shop_login_btn()

        #대시보드 진입 확인
        assert self.driver.title == self.login_expect_title
        log.info(self.driver.title)

        time.sleep(1)

