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
    seg_expect_title = "세그먼트 타겟팅 :: GROOBEE"
    modal_title = '세그먼트 삭제'

    @pytest.mark.login
    def test_login(self, driver, login):
        ## 로그인 확인
        assert driver.title == self.login_expect_title
    
    @pytest.mark.del_seg
    def test_delete_seg(self, driver):
        self.groobee.click_segment_menu()
        assert driver.title == self.seg_expect_title

        self.groobee.send_search_word(text='[AUTO]')
        
        assert self.modal_title == self.groobee.cehck_modal_title()
        self.groobee.click_modal_ok_btn()