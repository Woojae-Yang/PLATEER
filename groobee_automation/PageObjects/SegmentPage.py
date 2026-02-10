import time
import pytest

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from PageObjects.GroobeeActions import GroobeeActions
from utilities.BaseClass import BaseClass

class SegmentPage(GroobeeActions):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    # ------------------------------ element 선언 ------------------------------
    
    # 데이터 테이블 영역 : 참조할 항목이 없어서 어쩔 수 없이 절대경로 입력
    seg_search_bar = (By.XPATH, "/html/body/div/div[3]/div/div/div/div[3]/div/div[1]/div[2]/div/div/div/input")
    empty_msg = (By.XPATH, "/html/body/div/div[3]/div/div/div/div[3]/div/div[2]/div[1]/div[2]/div[1]/div/div/div")

    # 도구모음
    top_tools_btn = (By.XPATH, "//div[@data-rowindex='0']//button[.//*[@data-testid='MoreHorizIcon']]")
    tools_del_btn = (By.XPATH, "//li[contains(normalize-space(.), '삭제')]")
    tools_copy_btn = (By.XPATH, "//li[contains(normalize-space(.), '복사')]")
    modal_title = (By.XPATH, "//div[@role='dialog']//h2[contains(text(), '세그먼트 삭제')]")
    modal_ok_btn = (By.XPATH, "(//div[@role='dialog']//button[contains(normalize-space(.), '확인')])[last()]")
    modal_cancel_btn = (By.XPATH, "//div[@role='dialog']//button[contains(normalize-space(.), '취소']")

    # 만들기
    createBtn = (By.XPATH, "//button[contains(text(),'만들기')]")

    # 세그먼트
    seg_title = (By.XPATH, "//h1[contains(text(),'새로운 세그먼트 만들기')]")
    seg_name = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 40자']")
    seg_des = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 400자']")

    # 타겟 설정
    range_onsite_web = (By.XPATH, "//label[contains(., '온사이트(웹/하이브리드)')]//span[1]")
    range_onsite_native = (By.XPATH, "//label[contains(., '온사이트(네이티브)')]//span[1]")
    range_offsite = (By.XPATH, "//label[contains(., '오프사이트')]//span[1]")
    time_past = (By.XPATH, "//label[contains(., '과거')]//span[1]")
    time_now = (By.XPATH, "//label[contains(., '현재')]//span[1]")
    time_cross = (By.XPATH, "//label[contains(., '과거 x 현재')]//span[1]")
    mix_andor = (By.XPATH, "//label[contains(., 'AND/OR')]//span[1]")
    mix_strong = (By.XPATH, "//label[contains(., '시퀀스(강)')]//span[1]")
    mix_weak = (By.XPATH, "//label[contains(., '시퀀스(약)')]//span[1]")

    # 세그먼트 변수 추가 버튼
    add_seg_btn = (By.XPATH, "//button[contains(text(), '세그먼트 변수')]")

    ### `과거 x 현재` 시점에서 활용
    past_div = (By.XPATH, "//h6[text()='과거']/ancestor::div[contains(@class, 'MuiPaper-root')][1]")
    present_div = (By.XPATH, "//h6[text()='현재']/ancestor::div[contains(@class, 'MuiPaper-root')][1]")

    # 세그먼트 변수 RNB
    rnb_title_elem = (By.XPATH, "//h2[contains(., '세그먼트 변수')]")
    add_seg1 = (By.XPATH, "(//button[@type='button'][contains(text(),'세그먼트 변수')])[1]")
    add_seg2 = (By.XPATH, "(//button[@type='button'][contains(text(),'세그먼트 변수')])[2]")
    and_Btn = (By.XPATH, "//button[normalize-space()='AND']")
    rnb_xBtn = (By.XPATH, "//span[normalize-space()='close_icon']")
    rnb_system = (By.XPATH, "//h6[contains(text(), '시스템')]")
    rnb_system_os = (By.XPATH, "//h6[contains(text(), '접속 OS')]")
    rnb_system_device = (By.XPATH, "//h6[contains(text(),'접속 디바이스')]")
    rnb_system_browser = (By.XPATH, "//h6[contains(text(),'브라우저 유형')]")
    rnb_system_language = (By.XPATH, "//h6[contains(text(),'브라우저 언어')]")
    rnb_visit_rec = (By.XPATH, "//h6[contains(text(), '방문 이력')]")
    rnb_visit_freq = (By.XPATH, "//h6[contains(text(), '방문 횟수')]")
    rnb_visit_rec_first = (By.XPATH, "//h6[contains(text(),'첫 방문')]")
    rnb_visit_rec_week = (By.XPATH, "//h6[contains(text(),'방문 요일')]")
    rnb_visit_rec_time = (By.XPATH, "//h6[contains(text(),'방문 시간대')]")
    rnb_order_rec = (By.XPATH, "//h6[contains(text(), '주문 이력')]")
    rnb_campaign_rec = (By.XPATH, "//h6[contains(text(), '캠페인 이력')]")
    rnb_visitors = (By.XPATH, "//h6[contains(text(), '방문자 유형')]")
    rnb_visitors_member = (By.XPATH, "//h6[contains(text(),'회원 방문자')]")
    rnb_visitors_login = (By.XPATH, "//h6[contains(text(),'로그인 방문자')]")
    rnb_visitors_gender = (By.XPATH, "//h6[contains(text(),'회원 성별')]")
    rnb_visit_act = (By.XPATH, "//h6[contains(text(), '방문 행동')]")
    rnb_visit_page = (By.XPATH, "//h6[contains(text(), '방문 페이지')]")
    rnb_cart_act = (By.XPATH, "//h6[contains(text(), '장바구니 행동')]")
    rnb_cart_prod_nm = (By.XPATH, "//h6[contains(text(), '담은 상품명')]")
    rnb_order_act = (By.XPATH, "//h6[contains(text(), '주문 행동')]")
    rnb_custom = (By.XPATH, "//h6[contains(text(), '커스텀')]")
    rnb_choose = (By.XPATH, "//button[contains(text(),'선택')]")
    rnb_order_cnt = (By.XPATH, "//h6[contains(text(), '주문 횟수')]")

    # 세그먼트 변수 설정(설정할 값 실제 작성)
    seg_setting1 = (By.XPATH, "(//div[contains(@role,'combobox')])[1]")
    seg_setting1_pc = (By.XPATH, "//li[normalize-space()='PC']")
    seg_setting1_wed = (By.XPATH, "//li[contains(text(),'수')]")
    seg_setting1_android = (By.XPATH, "//li[normalize-space()='Android']")
    seg_setting2 = (By.XPATH, "(//div[contains(@role,'combobox')])[2]")
    seg_setting2_yes = (By.XPATH, "//li[contains(text(),'일 때')]")
    seg_setting3 = (By.XPATH, "(//div[contains(@role,'combobox')])[3]")
    seg_setting3_ios = (By.XPATH, "//li[normalize-space()='iOS']")
    seg_setting4 = (By.XPATH, "(//div[contains(@role,'combobox')])[4]")
    seg_setting4_yes = (By.XPATH, "//li[contains(text(),'일 때')]")
    seg_setting_or = (By.XPATH, "//button[normalize-space()='OR']")
    seg_setting_and = (By.XPATH, "//button[normalize-space()='AND']")

    # 완료
    cancelBtn = (By.XPATH, "//button[contains(text(),'취소')]")
    saveBtn = (By.XPATH, "//button[contains(text(),'저장')]")

    # ------------------------------ action + wait ------------------------------
    # 만들기
    def click_create_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.createBtn, timeout).click()

    # 서치바 입력하기
    def send_search_word(self, text, timeout=10):
        search_bar = BaseClass.wait_clickable(self.driver, self.seg_search_bar, timeout)
        search_bar.click()
        time.sleep(1)
        search_bar.send_keys(text)
        search_bar.send_keys(Keys.ENTER)
        time.sleep(1)
    
    # 검색 결과 없음 안내 문구
    def get_empty_msg(self, timeout=10):
        return BaseClass.wait_visible(self.driver, self.empty_msg, timeout)

    # 도구모음
    def click_top_tools_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.top_tools_btn, timeout).click()
        time.sleep(1)
    def click_tools_del_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.tools_del_btn, timeout).click()
        time.sleep(1)
    def click_tools_copy_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.tools_copy_btn, timeout).click()
        time.sleep(1)
    def check_modal_title(self, timeout=10):
        return BaseClass.wait_visible(self.driver, self.modal_title, timeout).text
    def click_modal_ok_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.modal_ok_btn, timeout).click()
        time.sleep(0.5)
    

    # 세그먼트 기본 정보 입력
    def send_seg_name(self, text, timeout=10):
        elem = BaseClass.wait_clickable(self.driver, self.seg_name, timeout)
        elem.click()
        elem.clear()
        elem.send_keys(text)
    def send_seg_des(self, text, timeout=10):
        elem = BaseClass.wait_clickable(self.driver, self.seg_des, timeout)
        elem.click()
        elem.clear()
        elem.send_keys(text)
    def get_seg_name(self, timeout=10):
        return BaseClass.wait_visible(self.driver, self.seg_name, timeout).get_attribute("value")

    # 타겟 설정
    def click_range_onsite_web(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.range_onsite_web, timeout).click()
    def click_range_onsite_native(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.range_onsite_native, timeout).click()
    def click_range_offsite(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.range_offsite, timeout).click()
    def click_time_past(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.time_past, timeout).click()
    def click_time_now(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.time_now, timeout).click()
    def click_time_cross(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.time_cross, timeout).click()
    def click_mix_andor(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.mix_andor, timeout).click()
    def click_mix_strong(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.mix_strong, timeout).click()
    def click_mix_weak(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.mix_weak, timeout).click()

    # 세그먼트 변수 RNB 열기
    def click_add_seg_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.add_seg_btn, timeout).click()

    # 세그먼트 변수 RNB
    def click_add_seg1(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.add_seg1, timeout).click()
    def click_add_seg2(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.add_seg2, timeout).click()
    def click_and_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.and_Btn, timeout).click()
    def click_rnb_xbtn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_xBtn, timeout).click()
    def click_rnb_system(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_system, timeout).click()
    def click_rnb_system_os(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_system_os, timeout).click()
    def click_rnb_system_device(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_system_device, timeout).click()
    def click_rnb_system_browser(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_system_browser, timeout).click()
    def click_rnb_system_language(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_system_language, timeout).click()
    def click_rnb_visit_rec(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_visit_rec, timeout).click()
    def click_rnb_visit_freq(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_visit_freq, timeout).click()
    def click_rnb_visit_rec_first(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_visit_rec_first, timeout).click()
    def click_rnb_visit_rec_week(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_visit_rec_week, timeout).click()
    def click_rnb_visit_rec_time(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_visit_rec_time, timeout).click()
    def click_rnb_order_rec(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_order_rec, timeout).click()
    def click_rnb_campaign_rec(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_campaign_rec, timeout).click()
    def click_rnb_visitors(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_visitors, timeout).click()
    def click_rnb_visitors_member(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_visitors_member, timeout).click()
    def click_rnb_visitors_login(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_visitors_login, timeout).click()
    def click_rnb_visitors_gender(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_visitors_gender, timeout).click()
    def click_rnb_visit_act(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_visit_act, timeout).click()
    def click_rnb_visit_page(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_visit_page, timeout).click()
    def click_rnb_cart_act(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_cart_act, timeout).click()
    def click_rnb_cart_prod_nm(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_cart_prod_nm, timeout).click()
    def click_rnb_order_act(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_order_act, timeout).click()
    def click_rnb_custom(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_custom, timeout).click()
    def click_rnb_choose(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_choose, timeout).click()
        time.sleep(1.5)
    def click_rnb_order_cnt(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_order_cnt, timeout).click()

    # 세그먼트 변수 설정(설정할 값 실제 작성)
    def click_seg_setting1(self, timeout=10):
        elem = BaseClass.wait_clickable(self.driver, self.seg_setting1, timeout)
        elem.click()
        return elem
    def click_seg_setting1_pc(self, timeout=10):
        elem = BaseClass.wait_clickable(self.driver, self.seg_setting1_pc, timeout)
        elem.click()
        return elem
    def click_seg_setting1_wed(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_setting1_wed, timeout).click()
    def click_seg_setting1_android(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_setting1_android, timeout).click()
    def click_seg_setting2(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_setting2, timeout).click()
    def click_seg_setting2_yes(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_setting2_yes, timeout).click()
    def click_seg_setting3(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_setting3, timeout).click()
    def click_seg_setting3_ios(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_setting3_ios, timeout).click()
    def click_seg_setting4(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_setting4, timeout).click()
    def click_seg_setting4_yes(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_setting4_yes, timeout).click()
    def click_seg_setting_or(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_setting_or, timeout).click()
    def click_seg_setting_and(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_setting_and, timeout).click()

    # 완료
    def click_cancel_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.cancelBtn, timeout).click()
    def click_save_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.saveBtn, timeout).click()


    ######################################################
    # 테스트에 활용되는 함수들
    ######################################################

    # target_map에서 category와 value에 맞는 함수를 찾아 실행하는 함수
    def select_target_radio(self, category, value, target_map):
        if value:
            if value is None or value == "None":
                return 
            try:
                print(f"[DEBUG] Clicking {category}: {value}")
                target_map[category][value]()
                time.sleep(0.5) # 라디오 버튼 클릭 후 UI 반응 대기
            except KeyError:
                pytest.fail(f"매핑 테이블에 '{value}' 키가 없습니다.")

    # rnb_map에서 var_name에 맞는 시퀀스를 찾아 실행하는 실행 함수 
    def navigate_rnb(self, var_name, rnb_map):
        if var_name in rnb_map:
            for func in rnb_map[var_name]:
                func()
        time.sleep(1.5)

    # 선택한 세그먼트 유형의 세부 설정
    def select_seg_details(self, v1, v2):
    ### 하나만 있거나, v1/v2 둘 다 있거나, 둘 다 없는 경우 모두 처리 가능
    ### 실행할 메서드와 매칭될 값을 리스트로 관리
        actions = [(self.click_seg_setting1, v1),(self.click_seg_setting2, v2)]
        for i, (click_func, val) in enumerate(actions, start=1):
            if not val: continue

            try:
            # 설정할 변수 요소 클릭 : click_* 함수에서 반환한 요소 값 할당
                container = click_func()
                time.sleep(0.8)

                if not container:
                    var_elem = f"(//div[contains(@class, 'MuiInputBase-root')])[{i}]"
                    container = BaseClass.wait_clickable(self.driver, (By.XPATH, var_elem), timeout=10)

                # 판별 및 실행
                textareas = container.find_elements(By.TAG_NAME, "textarea")

                if textareas:
                    print(f"[DEBUG] {i}번 영역: 입력형 처리 -> {val}")
                    textareas[0].send_keys(val)
                    textareas[0].send_keys(Keys.ENTER)

                else:
                    print(f"[DEBUG] {i}번 영역: 선택형 처리 -> {val}")
                    li_xpath = f"//li[contains(., '{val}')]"
                    # 일반 클릭(.click())이 가로채기 에러가 나면 JS 클릭으로 우회
                    try:
                        BaseClass.wait_clickable(self.driver, (By.XPATH, li_xpath), timeout=10).click()
                    except Exception:
                        li_elem = BaseClass.wait_clickable(self.driver, (By.XPATH, li_xpath), timeout=10)
                        self.driver.execute_script("arguments[0].click();", li_elem)
            except Exception as e:
                print(f"[ERROR] 상세설정 {i}번 처리 중 오류: {e}")
            time.sleep(0.5)


    # 생성된 세그먼트 리스트
    def get_seg_list_item(self, seg_name):
        return self.driver.find_element(By.XPATH, f"//p[contains(text(), '{seg_name}')]")
   
    # 생성된 세그먼트 데이터테이블의 맨 위 row에 대한 정보 가져오기
    def get_seg_info(self):
        seg_elem = "//div[@data-rowindex='0']"
        return {
            "name": self.driver.find_element(By.XPATH, f"{seg_elem}//div[@data-field='segmentNm']").text,
            "used": self.driver.find_element(By.XPATH, f"{seg_elem}//div[@data-field='used']").text,
            "range": self.driver.find_element(By.XPATH, f"{seg_elem}//div[@data-field='range']").text,
            "segmentTime": self.driver.find_element(By.XPATH, f"{seg_elem}//div[@data-field='segmentTime']").text,
            "segmentCheckCd": self.driver.find_element(By.XPATH, f"{seg_elem}//div[@data-field='segmentCheckCd']").text,
            "reg_date": self.driver.find_element(By.XPATH, f"{seg_elem}//div[@data-field='regDtm']").text
    }

    ### `과거 x 현재` 시점에서 활용
    def click_var_btn_in_scope(self, scope_locator):
        parent = BaseClass.wait_visible(self.driver, scope_locator)
        parent.find_element(*self.add_seg_btn).click()
        time.sleep(0.7)