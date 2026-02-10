import pytest
import time
from datetime import datetime

from PageObjects.SegmentPage import SegmentPage
from utilities.BaseClass import BaseClass

from selenium.webdriver.common.by import By


@pytest.mark.usefixtures("driver", "login")
class TestSegCreateCross:

    # (범위, 시점, 조합, 세그먼트 변수 과거, 과거값1, 과거값2, 세그먼트 변수 현재, 현재값3, 현재값4) : 추후 csv로 변환하여 관리 가능
    DECISION_TABLE = [
    ("온사이트(웹/하이브리드)", "과거 x 현재", None, "주문 횟수", "5", "이상", "로그인 방문자", None, None),
    ("온사이트(네이티브)", "과거 x 현재", None, "주문 횟수", "5", "이상", "로그인 방문자", None, None)
    ]

    @pytest.fixture(autouse=True)
    def setup_pages(self, driver):
        ## 함수 실행 전 자동으로 호출되어 페이지 객체 초기화
        self.groobee = SegmentPage(driver)

        ## 타겟 설정 매핑 초기화
        self.target_map = {
            "range": {
                "온사이트(웹/하이브리드)": self.groobee.click_range_onsite_web,
                "온사이트(네이티브)": self.groobee.click_range_onsite_native
            },
            "time": {
                "과거 x 현재": self.groobee.click_time_cross
            },
            "condition": {
                "AND/OR": self.groobee.click_mix_andor
            }
        }
        # 2. RNB 변수 선택 매핑 (함수 시퀀스)
        self.rnb_map = {
            "주문 횟수": [self.groobee.click_rnb_order_rec, self.groobee.click_rnb_order_cnt],
            "로그인 방문자": [self.groobee.click_rnb_visitors, self.groobee.click_rnb_visitors_login]
        }

    login_expect_title = "대시보드 :: GROOBEE"
    seg_expect_title = "세그먼트 타겟팅 :: GROOBEE"
    seg_description = 'Automation Testing'

    @pytest.mark.login
    def test_login(self, driver, login):
        ## 로그인 확인
        assert driver.title == self.login_expect_title
    
    @pytest.mark.seg
    @pytest.mark.parametrize("range_v, time_v, cond_v, past_var, past_v1, past_v2, n_var, n_v1, n_v2", DECISION_TABLE)
    def test_seg_create_flow(self, driver, range_v, time_v, cond_v, past_var, past_v1, past_v2, n_var, n_v1, n_v2):
        seg_title = f"[AUTO]seg_{datetime.now().strftime('%H%M%S')}Cross"
        
        ## LNB 세그먼트 페이지 진입
        self.groobee.click_segment_menu()

        # 만들기 진입
        self.groobee.click_create_btn()
        time.sleep(1.5)
        assert BaseClass.wait_visible(driver, self.groobee.seg_title).is_displayed()

        # 세그먼트명, 상세설명 입력
        self.groobee.send_seg_name(seg_title)
        self.groobee.send_seg_des(self.seg_description)
        time.sleep(1.5)

        # 타겟 설정
        self.groobee.select_target_radio("range", range_v, self.target_map)
        self.groobee.select_target_radio("time", time_v, self.target_map)
        #self.groobee.select_target_radio("condition", cond_v, self.target_map)
        
        # 과거 세그먼트 변수 설정
        self.groobee.click_var_btn_in_scope(self.groobee.past_div)
        assert BaseClass.wait_visible(driver, self.groobee.rnb_title_elem).is_displayed()
        ### 세그먼트 변수 RNB
        self.groobee.navigate_rnb(past_var, self.rnb_map)
        self.groobee.click_rnb_choose()
        ### 선택한 세그먼트 변수 상세 설정
        self.groobee.select_seg_details(past_v1, past_v2)

        # 현재 세그먼트 변수 설정
        self.groobee.click_var_btn_in_scope(self.groobee.present_div)
        assert BaseClass.wait_visible(driver, self.groobee.rnb_title_elem).is_displayed()
        ### 세그먼트 변수 RNB
        self.groobee.navigate_rnb(n_var, self.rnb_map)
        self.groobee.click_rnb_choose()
        ### 선택한 세그먼트 변수 상세 설정
        self.groobee.select_seg_details(n_v1, n_v2)
        
        # 저장 버튼 클릭
        self.groobee.click_save_btn()
        time.sleep(1)

        ######################################################
        # [검증 영역] 매 케이스마다 즉시 확인 
        ######################################################
        seg_info = self.groobee.get_seg_info()

        assert seg_title in seg_info['name'], f"이름 불일치: {seg_info['name']}"
        assert seg_info['range'] == range_v, f"범위 불일치: {range_v}"
        if time_v is not None: # [타겟설정 > 시점]이 None인 경우에 대한 방어로직
            assert seg_info['segmentTime'] == time_v, f"시점 불일치: {time_v}"
        if cond_v is not None: # [타겟설정 > 조합]이 None인 경우에 대한 방어로직
            assert seg_info['segmentCheckCd'] == cond_v, f"조건 불일치: {cond_v}"



