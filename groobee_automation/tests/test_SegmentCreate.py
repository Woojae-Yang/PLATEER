import pytest
import time
from datetime import datetime

from PageObjects.SegmentPage import SegmentPage
from utilities.BaseClass import BaseClass

from selenium.webdriver.common.by import By

@pytest.mark.usefixtures("driver", "login")
class TestSegCreate(BaseClass):
    now = datetime.now()
    ymd = now.strftime('%y-%m-%d')
    hms = now.strftime('%H:%M:%S')
    login_expect_title = "대시보드 :: GROOBEE"
    seg_title = f'[AUTO]segment{ymd}_{hms}'
    seg_description = 'Automation Testing'
    default_range = '온사이트(웹/하이브리드)'
    default_time = '과거'
    default_seg_cd = 'AND/OR'

    @pytest.fixture(autouse=True)
    def setup_pages(self, driver):
        ## 함수 실행 전 자동으로 호출되어 페이지 객체 초기화
        self.groobee = SegmentPage(driver)

    @pytest.mark.login
    def test_login(self, driver, login):
        ## 로그인 확인
        assert driver.title == self.login_expect_title
    
    @pytest.mark.seg
    def test_seg_create_flow(self, driver):
        ## 세그먼트 페이지 진입
        self.groobee.click_segment_menu()
        target_title_elem = (By.XPATH, "//h1[contains(text(),'세그먼트 타겟팅')]")
        assert BaseClass.wait_visible(driver, target_title_elem).is_displayed()

        # 만들기 진입
        self.groobee.click_create_btn()
        time.sleep(1.5)
        assert BaseClass.wait_visible(driver, self.groobee.seg_title).is_displayed()

        # 세그먼트명, 상세설명 입력
        self.groobee.send_seg_name(self.seg_title)
        self.groobee.send_seg_des(self.seg_description)
        time.sleep(1.5)

        # 타겟 설정 부분은 default 유지
        
        # 세그먼트 변수 btn 클릭
        self.groobee.click_add_seg_btn()
        time.sleep(2)
        rnb_title_elem = (By.XPATH, "//h2[contains(., '세그먼트 변수')]")
        assert BaseClass.wait_visible(driver, rnb_title_elem).is_displayed()

        # 세그먼트 변수 RNB
        ## 시스템 클릭
        self.groobee.click_rnb_system()
        # 브라우저 유형 클릭
        self.groobee.click_rnb_system_browser()

        self.groobee.click_rnb_choose()
        time.sleep(1)

        # 선택한 세그먼트 변수 상세 설정
        self.groobee.click_seg_setting1()
        driver.find_element(By.XPATH, "//li[contains(text(),'Chrome')]").click()
        self.groobee.click_seg_setting2()
        driver.find_element(By.XPATH, "//li[contains(text(),'일 때')]").click()
        
        self.groobee.click_save_btn()
        time.sleep(1)

    @pytest.mark.seg
    def test_created_seg(self, driver):
        seg_info = self.groobee.get_seg_info()

        assert seg_info['name'] == self.seg_title
        assert seg_info['range'] == self.default_range
        assert seg_info['segmentTime'] == self.default_time
        assert seg_info ['segmentCheckCd'] == self.default_seg_cd












