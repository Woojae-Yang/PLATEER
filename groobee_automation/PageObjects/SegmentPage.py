from selenium.webdriver.common.by import By

class SegmentPage:

    def __init__(self, driver):
        self.driver = driver

    # -------------------------element 선언 영역-------------------------
    # 세그먼트 타겟팅 메뉴
    segmentMenu = (By.XPATH, "//a[@href='/segment']")

    # 만들기
    createBtn = (By.XPATH, "//button[contains(text(),'만들기')]")

    # 관리 도구
    tools_icon = (By.XPATH, "//div[@class='MuiDataGrid-row']//button[@type='button']")
    update_icon = (By.XPATH, "//div[contains(text(),'수정')]")
    copy_icon = (By.XPATH, "//div[contains(text(),'복사')]")
    download_icon = (By.XPATH, "//div[contains(text(),'방문자 리스트 다운로드')]")
    delete_icon = (By.XPATH, "//div[contains(text(),'삭제')]")
    delete_icon_cancel = (By.XPATH, "//button[contains(text(),'취소')]")
    delete_icon_confirm = (By.XPATH, "//button[contains(text(),'확인')]")

    # 세그먼트
    seg_title = (By.XPATH, "//h1[contains(text(),'새로운 세그먼트 만들기')]")
    seg_name = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 40자']")
    seg_des = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 400자']")

    # 타겟 설정
    range_onsite_web = (By.XPATH, "//input[@value='ON']")
    range_onsite_native = (By.XPATH, "//input[@value='IN']")
    range_offsite = (By.XPATH, "//input[@value='OF']")
    time_past = (By.XPATH, "//input[@value='PA']")
    time_now = (By.XPATH, "//input[@value='PR']")
    time_cross = (By.XPATH, "//input[@value='PP']")
    mix_andor = (By.XPATH, "//input[@value='AO']")
    mix_strong = (By.XPATH, "//input[@value='S1']")
    mix_weak = (By.XPATH, "//input[@value='S2']")

    # 세그먼트 변수 RNB
    add_seg1 = (By.XPATH, "(//button[@type='button'][contains(text(),'세그먼트 변수')])[1]")
    add_seg2 = (By.XPATH, "(//button[@type='button'][contains(text(),'세그먼트 변수')])[2]")
    and_Btn = (By.XPATH, "//button[normalize-space()='AND']")
    rnb_xBtn = (By.XPATH, "//span[normalize-space()='close_icon']")
    rnb_system = (By.XPATH, "//h6[contains(text(), '시스템')]")
    rnb_system_device = (By.XPATH, "//h6[contains(text(),'접속 디바이스')]")
    rnb_system_browser = (By.XPATH, "//h6[contains(text(),'브라우저 유형')]")
    rnb_system_language = (By.XPATH, "//h6[contains(text(),'브라우저 언어')]")
    rnb_visit_rec = (By.XPATH, "//h6[contains(text(), '방문 이력')]")
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
    rnb_cart_act = (By.XPATH, "//h6[contains(text(), '장바구니 행동')]")
    rnb_order_act = (By.XPATH, "//h6[contains(text(), '주문 행동')]")
    rnb_custom = (By.XPATH, "//h6[contains(text(), '커스텀')]")
    rnb_choose = (By.XPATH, "//button[contains(text(),'선택')]")

    # 세그먼트 변수 설정(설정할 값 실제 작성)
    seg_setting1 = (By.XPATH, "(//div[contains(@role,'combobox')])[1]")
    seg_setting1_pc = (By.XPATH, "//li[normalize-space()='PC']")
    seg_setting1_wed = (By.XPATH, "//li[contains(text(),'수')]")
    seg_setting2 = (By.XPATH, "(//div[contains(@role,'combobox')])[2]")
    seg_setting2_yes = (By.XPATH, "//li[contains(text(),'일 때')]")

    # 완료
    cancelBtn = (By.XPATH, "//button[contains(text(),'취소')]")
    saveBtn = (By.XPATH, "//button[contains(text(),'저장')]")

    # -------------------------동작 선언 영역-------------------------
    # 세그먼트 타겟팅 메뉴
    def click_segment_menu(self):
        return self.driver.find_element(*SegmentPage.segmentMenu)

    # 만들기
    def click_create_btn(self):
        return self.driver.find_element(*SegmentPage.createBtn)

    # 관리 도구
    def click_tools_icon(self):
        return self.driver.find_element(*SegmentPage.tools_icon)
    def click_update_icon(self):
        return self.driver.find_element(*SegmentPage.update_icon)
    def click_copy_icon(self):
        return self.driver.find_element(*SegmentPage.copy_icon)
    def click_download_icon(self):
        return self.driver.find_element(*SegmentPage.download_icon)
    def click_delete_icon(self):
        return self.driver.find_element(*SegmentPage.delete_icon)
    def click_delete_icon_cancel(self):
        return self.driver.find_element(*SegmentPage.delete_icon_cancel)
    def click_delete_icon_confirm(self):
        return self.driver.find_element(*SegmentPage.delete_icon_confirm)

    # 삭제할 세그먼트 찾기
    @staticmethod
    def click_tools_icon_by_name(seg_element, driver):
        # row 찾기
        row = seg_element.find_element(By.XPATH, "./ancestor::div[contains(@class,'MuiDataGrid-row')]")

        # row index 저장
        row_index = row.get_attribute("data-rowindex")

        # 버튼 찾기
        pinned_container = driver.find_element(By.XPATH, "//div[contains(@class,'MuiDataGrid-pinnedColumns--right')]")
        buttons = pinned_container.find_elements(By.XPATH, ".//button[contains(@class,'MuiIconButton-root')]")

        # 버튼과 row index 매칭
        target_btn = None
        for btn in buttons:
            btn_row = btn.find_element(By.XPATH, "./ancestor::div[contains(@class,'MuiDataGrid-row')]")
            btn_row_index = btn_row.get_attribute("data-rowindex")
            if btn_row_index == row_index:
                target_btn = btn
                break

        return target_btn

    # 세그먼트 입력
    def send_seg_name(self):
        return self.driver.find_element(*SegmentPage.seg_name)
    def send_seg_des(self):
        return self.driver.find_element(*SegmentPage.seg_des)

    # 타겟 설정
    def click_range_onsite_web(self):
        return self.driver.find_element(*SegmentPage.range_onsite_web)
    def click_range_onsite_native(self):
        return self.driver.find_element(*SegmentPage.range_onsite_native)
    def click_range_offsite(self):
        return self.driver.find_element(*SegmentPage.range_offsite)
    def click_time_past(self):
        return self.driver.find_element(*SegmentPage.time_past)
    def click_time_now(self):
        return self.driver.find_element(*SegmentPage.time_now)
    def click_time_cross(self):
        return self.driver.find_element(*SegmentPage.time_cross)
    def click_mix_andor(self):
        return self.driver.find_element(*SegmentPage.mix_andor)
    def click_mix_strong(self):
        return self.driver.find_element(*SegmentPage.mix_strong)
    def click_mix_weak(self):
        return self.driver.find_element(*SegmentPage.mix_weak)

    # 세그먼트 변수 RNB
    def click_add_seg1(self):
        return self.driver.find_element(*SegmentPage.add_seg1)
    def click_add_seg2(self):
        return self.driver.find_element(*SegmentPage.add_seg2)
    def click_and_btn(self):
        return self.driver.find_element(*SegmentPage.and_Btn)
    def click_rnb_xbtn(self):
        return self.driver.find_element(*SegmentPage.rnb_xBtn)
    def click_rnb_system(self):
        return self.driver.find_element(*SegmentPage.rnb_system)
    def click_rnb_system_device(self):
        return self.driver.find_element(*SegmentPage.rnb_system_device)
    def click_rnb_system_browser(self):
        return self.driver.find_element(*SegmentPage.rnb_system_browser)
    def click_rnb_system_language(self):
        return self.driver.find_element(*SegmentPage.rnb_system_language)
    def click_rnb_visit_rec(self):
        return self.driver.find_element(*SegmentPage.rnb_visit_rec)
    def click_rnb_visit_rec_first(self):
        return self.driver.find_element(*SegmentPage.rnb_visit_rec_first)
    def click_rnb_visit_rec_week(self):
        return self.driver.find_element(*SegmentPage.rnb_visit_rec_week)
    def click_rnb_visit_rec_time(self):
        return self.driver.find_element(*SegmentPage.rnb_visit_rec_time)
    def click_rnb_order_rec(self):
        return self.driver.find_element(*SegmentPage.rnb_order_rec)
    def click_rnb_campaign_rec(self):
        return self.driver.find_element(*SegmentPage.rnb_campaign_rec)
    def click_rnb_visitors(self):
        return self.driver.find_element(*SegmentPage.rnb_visitors)
    def click_rnb_visitors_member(self):
        return self.driver.find_element(*SegmentPage.rnb_visitors_member)
    def click_rnb_visitors_login(self):
        return self.driver.find_element(*SegmentPage.rnb_visitors_login)
    def click_rnb_visitors_gender(self):
        return self.driver.find_element(*SegmentPage.rnb_visitors_gender)
    def click_rnb_visit_act(self):
        return self.driver.find_element(*SegmentPage.rnb_visit_act)
    def click_rnb_cart_act(self):
        return self.driver.find_element(*SegmentPage.rnb_cart_act)
    def click_rnb_order_act(self):
        return self.driver.find_element(*SegmentPage.rnb_order_act)
    def click_rnb_custom(self):
        return self.driver.find_element(*SegmentPage.rnb_custom)
    def click_rnb_choose(self):
        return self.driver.find_element(*SegmentPage.rnb_choose)

    # 세그먼트 변수 설정(설정할 값 실제 작성)
    def click_seg_setting1(self):
        return self.driver.find_element(*SegmentPage.seg_setting1)
    def click_seg_setting1_pc(self):
        return self.driver.find_element(*SegmentPage.seg_setting1_pc)
    def click_seg_setting1_wed(self):
        return self.driver.find_element(*SegmentPage.seg_setting1_wed)
    def click_seg_setting2(self):
        return self.driver.find_element(*SegmentPage.seg_setting2)
    def click_seg_setting2_yes(self):
        return self.driver.find_element(*SegmentPage.seg_setting2_yes)

    # 완료
    def click_cancel_btn(self):
        return self.driver.find_element(*SegmentPage.cancelBtn)
    def click_save_btn(self):
        return self.driver.find_element(*SegmentPage.saveBtn)

    # 생성된 세그먼트 리스트
    def get_seg_list_item(self, seg_name):
        return self.driver.find_element(By.XPATH, f"//p[contains(text(), '{seg_name}')]")