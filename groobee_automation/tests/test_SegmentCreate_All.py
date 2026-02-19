import pytest
import time
from datetime import datetime

from PageObjects.SegmentPage import SegmentPage
from utilities.BaseClass import BaseClass

from selenium.webdriver.common.by import By


@pytest.mark.usefixtures("driver", "login")
class TestSegCreateCross:

    # (범위, 시점, 조합, 세그먼트 변수1, 값1-1, 값1-2, 세그먼트 변수2, 값2-1, 값2-2) : 추후 csv로 변환하여 관리 가능
    DECISION_TABLE = [
    # --- [단일 케이스] 뒤의 변수2 영역은 모두 None 처리 ---
    ("온사이트(웹/하이브리드)", "과거", None, "브라우저", "Chrome", "일 때", None, None, None),
    ("온사이트(웹/하이브리드)", "현재", "AND/OR", "브라우저", "Chrome", "아닐 때", None, None, None),
    ("온사이트(웹/하이브리드)", "현재", "시퀀스(강)", "방문 페이지", "https://groobee.net" , "일 때", None, None, None ),
    ("온사이트(웹/하이브리드)", "현재", "시퀀스(약)", "방문 페이지", "https://groobee.net" , "포함할 때", None, None, None ),
    ("온사이트(네이티브)", "과거", None, "첫 방문", None, None, None, None, None),
    ("온사이트(네이티브)", "현재", "AND/OR", "첫 방문", None, None, None, None, None),
    ("온사이트(네이티브)", "현재", "시퀀스(강)", "담은 상품명", "젤라또", "포함하지 않을 때", None, None, None),
    ("온사이트(네이티브)", "현재", "시퀀스(약)", "담은 상품명", "젤라또", "아닐 때", None, None, None),
    ("오프사이트", None, None, "로그인 방문자", None, None, None, None, None),

    # --- [크로스 케이스] 변수1(과거), 변수2(현재) 모두 사용 ---
    ("온사이트(웹/하이브리드)", "과거 x 현재", None, "주문 횟수", 5, "이상", "로그인 방문자", None, None),
    ("온사이트(네이티브)", "과거 x 현재", None, "첫 방문", None, None, "로그인 방문자", None, None)
    ]

    @pytest.fixture(autouse=True)
    def setup_pages(self, driver):
        ## 함수 실행 전 자동으로 호출되어 페이지 객체 초기화
        self.groobee = SegmentPage(driver)

        ## 타겟 설정 매핑 초기화
        self.target_map = {
            "range": {
                "온사이트(웹/하이브리드)": self.groobee.click_range_onsite_web,
                "온사이트(네이티브)": self.groobee.click_range_onsite_native,
                "오프사이트": self.groobee.click_range_offsite
            },
            "time": {
                "과거": self.groobee.click_time_past,
                "현재": self.groobee.click_time_now,
                "과거 x 현재": self.groobee.click_time_cross
            },
            "condition": {
                "AND/OR": self.groobee.click_mix_andor,
                "시퀀스(강)": self.groobee.click_mix_strong,
                "시퀀스(약)": self.groobee.click_mix_weak
            }
        }
        # 2. RNB 변수 선택 매핑 (함수 시퀀스)
        self.rnb_map = {
            "브라우저": [self.groobee.click_rnb_system, self.groobee.click_rnb_system_browser],
            "첫 방문": [self.groobee.click_rnb_visit_rec, self.groobee.click_rnb_visit_rec_first],
            "주문 횟수": [self.groobee.click_rnb_order_rec, self.groobee.click_rnb_order_cnt],
            "로그인 방문자": [self.groobee.click_rnb_visitors, self.groobee.click_rnb_visitors_login],
            "방문 페이지": [self.groobee.click_rnb_visit_act, self.groobee.click_rnb_visit_page],
            "담은 상품명": [self.groobee.click_rnb_cart_act, self.groobee.click_rnb_cart_prod_nm]
        }

    login_expect_title = "대시보드 :: GROOBEE"
    seg_expect_title = "세그먼트 타겟팅 :: GROOBEE"
    seg_description = 'Automation Testing'
    tag_text = "automation"

    @pytest.mark.login
    def test_login(self, driver, login):
        ## 로그인 확인
        assert driver.title == self.login_expect_title
    
    @pytest.mark.seg
    @pytest.mark.parametrize("range_v, time_v, cond_v, var1, v1_a, v1_b, var2, v2_a, v2_b", DECISION_TABLE)
    def test_seg_create_flow(self, driver, range_v, time_v, cond_v, var1, v1_a, v1_b, var2, v2_a, v2_b):
        driver.refresh()
        time.sleep(2)
        seg_title = f"[AUTO]seg_{datetime.now().strftime('%H%M%S')}{var1}"

        # ==========================================================
        # 1. 공통 진입 및 타겟 설정
        # ==========================================================
        
        ## LNB 세그먼트 페이지 진입
        self.groobee.click_segment_menu()
        assert driver.title == self.seg_expect_title

        # 만들기 진입
        self.groobee.click_create_btn()
        time.sleep(1.5)
        assert BaseClass.wait_visible(driver, self.groobee.seg_title).is_displayed()

        # 세그먼트명, 상세설명 입력
        self.groobee.send_seg_name(seg_title)
        self.groobee.send_seg_des(self.seg_description)
        time.sleep(1.5)
        
        # 태그 추가
        self.groobee.click_addtag_btn()
        self.groobee.send_tag_input(text = self.tag_text)
        self.groobee.click_tag_add()
        assert self.groobee.wait_tag_visible(self.tag_text)
        time.sleep(1.5)
        
        # 타겟 설정
        self.groobee.select_target_radio("range", range_v, self.target_map)
        self.groobee.select_target_radio("time", time_v, self.target_map)
        self.groobee.select_target_radio("condition", cond_v, self.target_map)
        
        # ==========================================================
        # 2. 시점에 따른 세그먼트 변수 분기 처리
        # ==========================================================
        
        if time_v == "과거 x 현재":
            # --- [A] 크로스 시나리오 처리 ---
            # 1. 과거 영역 설정 (var1 사용)
            past_scope = BaseClass.wait_visible(driver, self.groobee.past_div)
            self.groobee.click_var_btn_in_scope(self.groobee.past_div)
            self.groobee.navigate_rnb(var1, self.rnb_map)
            self.groobee.click_rnb_choose()
            self.groobee.select_seg_details(v1_a, v1_b, scope_elem=past_scope)
            
            # 2. 현재 영역 설정 (var2 사용)
            present_scope = BaseClass.wait_visible(driver, self.groobee.present_div)
            self.groobee.click_var_btn_in_scope(self.groobee.present_div)
            self.groobee.navigate_rnb(var2, self.rnb_map)
            self.groobee.click_rnb_choose()
            self.groobee.select_seg_details(v2_a, v2_b, scope_elem=present_scope)
            
        else:
            # --- [B] 단일 시나리오 처리 (과거, 현재, None) ---
            target_scope = None
            if time_v in ["과거", None]:
                target_scope = BaseClass.wait_visible(driver, self.groobee.past_div)
            elif time_v == "현재":
                target_scope = BaseClass.wait_visible(driver, self.groobee.present_div)

            # 단일 케이스는 변수 추가 버튼 로직이 다를 수 있음 (기존 코드 반영)
            self.groobee.click_add_seg_btn() 
            time.sleep(1)
            
            self.groobee.navigate_rnb(var1, self.rnb_map)
            self.groobee.click_rnb_choose()
            self.groobee.select_seg_details(v1_a, v1_b, scope_elem=target_scope)

        
        # ==========================================================
        # 3. 매 케이스마다 즉시 확인 (검증 영역)
        # ==========================================================
        
        total_cnt = self.groobee.get_total_visitor_cnt()
        if total_cnt == '-1':
            status = self.groobee.check_api_status("/v1/segment/size")
            print(f'status: {status}')
            assert status == 200, f"예상과 다른 응답코드: {status}"
        
        # 저장 버튼 클릭
        self.groobee.click_save_btn()
        time.sleep(1)

        seg_info = self.groobee.get_seg_info()

        assert seg_title in seg_info['name'], f"이름 불일치: {seg_info['name']}"
        assert seg_info['range'] == range_v, f"범위 불일치: {range_v}"
        if time_v is not None: # [타겟설정 > 시점]이 None인 경우에 대한 방어로직
            assert seg_info['segmentTime'] == time_v, f"시점 불일치: {time_v}"
        if cond_v is not None: # [타겟설정 > 조합]이 None인 경우에 대한 방어로직
            assert seg_info['segmentCheckCd'] == cond_v, f"조건 불일치: {cond_v}"


    @pytest.mark.copy_seg
    def test_copy_seg(self, driver):

        ## LNB 세그먼트 페이지 진입
        self.groobee.click_segment_menu()
        self.groobee.click_top_tools_btn()
        self.groobee.click_tools_copy_btn()
        assert self.groobee.get_seg_name()[-5:] == '-COPY'
