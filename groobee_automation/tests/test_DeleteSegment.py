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
    empty_expect_msg = "검색 결과가 없습니다."
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
        while True:
            try:
                if BaseClass.wait_visible(driver, self.groobee.top_tools_btn).is_displayed():
                    self.groobee.click_top_tools_btn()
                    self.groobee.click_tools_del_btn()
                    assert self.modal_title == self.groobee.cehck_modal_title()
                    self.groobee.click_modal_ok_btn()
                else:
                    empty_msg = self.groobee.get_empty_msg()
                    assert empty_msg == self.empty_expect_msg
                    break
            except Exception as e:
                print(f'[ERROR] {e}')
                break