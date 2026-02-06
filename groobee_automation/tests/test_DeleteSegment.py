import pytest
import time
from datetime import datetime

from PageObjects.SegmentPage import SegmentPage
from utilities.BaseClass import BaseClass

from selenium.webdriver.common.by import By

@pytest.mark.usefixtures("driver", "login")
class TestSegDel:

    @pytest.fixture(autouse=True)
    def setup_pages(self, driver):
        ## 함수 실행 전 자동으로 호출되어 페이지 객체 초기화
        self.groobee = SegmentPage(driver)

    login_expect_title = "대시보드 :: GROOBEE"
    seg_description = 'Automation Testing'
    @pytest.mark.login
    def test_login(self, driver, login):
        ## 로그인 확인
        assert driver.title == self.login_expect_title
    
    @pytest.mark.del_seg
    def test_delete_seg(self, driver):
        self.groobee.send_search_word(text='[AUTO]')