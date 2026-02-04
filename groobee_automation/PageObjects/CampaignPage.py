from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from PageObjects.GroobeeActions import GroobeeActions
from utilities.BaseClass import BaseClass

class CampaignPage(GroobeeActions):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    # -------------------------element 선언 영역-------------------------
    # 만들기
    createBtn = (By.XPATH, "//button[contains(text(),'만들기')]")
    createBtn_onsite = (By.XPATH, "//li[contains(text(),'온사이트 캠페인')]")
    createBtn_inapp = (By.XPATH, "//li[contains(text(),'인앱 메시지 캠페인')]")

    # 캠페인 입력
    cam_title = (By.XPATH, "//h1[contains(text(),'새로운 온사이트 캠페인 만들기')]")
    cam_name = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 40자']")
    cam_des = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 400자']")

    # 접속 유형
    type_pcweb = (By.XPATH, "//input[@value='PC']")
    type_mobile = (By.XPATH, "//input[@value='MO']")
    type_mobile_web = (By.XPATH, "//input[@value='MW']")
    type_mobile_app = (By.XPATH, "//input[@value='MA']")

    # 타겟 설정
    seg_load = (By.XPATH, "//button[contains(text(),'세그먼트 불러오기')]")

    # 세그먼트 불러오기 RNB(설정할 값 실제 작성)
    aiseg_tab = (By.XPATH, "//button[@id='basic-tab-0']")
    seg_tab = (By.XPATH, "//button[@id='basic-tab-1']")
    now_pc_seg = (By.XPATH, "//h6[contains(text(),'[QA] 온사이트웹-현재-PC접속 테스트 세그먼트')]")
    now_os_seg = (By.XPATH, "//h6[contains(text(),'[QA] 온사이트네이티브-현재-접속OS 테스트 세그먼트')]")
    selectBtn = (By.XPATH, "//button[contains(text(),'선택')]")

    # 추가
    addBtn = (By.XPATH, "//button[contains(text(),'추가')]")
    a_type = (By.XPATH, "//button[contains(text(),'A안')]")
    b_type = (By.XPATH, "//button[contains(text(),'B안')]")
    c_type = (By.XPATH, "//button[contains(text(),'C안')]")
    d_type = (By.XPATH, "//button[contains(text(),'D안')]")
    e_type = (By.XPATH, "//button[contains(text(),'E안')]")
    type_del_icon = (By.XPATH, "(//button[@type='button'])[11]")

    # 디자인 유형
    design_popup = (By.XPATH, "//input[@value='POPUP']")
    design_sticky_default = (By.XPATH, "//input[@value='STICKY_DEFAULT']")
    design_sticky_btn = (By.XPATH, "//input[@value='STICKY_BUTTON']")

    # URL 입력
    input_url = (By.XPATH, "//textarea[@placeholder='http:// 또는 https://를 포함한 URL']")
    image_map = (By.XPATH, "//input[@value='image-map']")

    # 내용 입력
    desBtn = (By.XPATH, "(//input[@type='checkbox'])[5]")
    input_des = (By.XPATH, "//textarea[@placeholder='한글 공백 포함 최대 80자']")
    sort_des = (By.XPATH, "(//button[@value='center'])[2]")
    input_txt20 = (By.XPATH, "//textarea[@placeholder='한글 공백 포함 최대 20자']")
    input_txt16 = (By.XPATH, "//textarea[@placeholder='한글 공백 포함 최대 16자']")
    input_txt40 = (By.XPATH, "//textarea[@placeholder='한글 공백 포함 최대 40자']")
    input_txt15 = (By.XPATH, "//textarea[@placeholder='한글 공백 포함 최대 15자']")
    bold_cbx = (By.XPATH, "(//input[@type='checkbox'])[1]")
    bold_cbx2 = (By.XPATH, "(//input[@type='checkbox'])[2]")
    bold_cbx3 = (By.XPATH, "(//input[@type='checkbox'])[3]")
    sort_mid = (By.XPATH, "//button[@value='1']")
    set_top = (By.XPATH, "//input[@value='48']")
    set_bottom = (By.XPATH, "//input[@value='80']")

    # 노출 위치 설정
    set_tl = (By.XPATH, "//input[@value='TL']")
    set_ml = (By.XPATH, "//input[@value='ML']")
    set_bl = (By.XPATH, "//input[@value='BL']")
    set_tc = (By.XPATH, "//input[@value='TC']")
    set_mc = (By.XPATH, "//input[@value='MC']")
    set_bc = (By.XPATH, "//input[@value='BC']")
    set_tr = (By.XPATH, "//input[@value='TR']")
    set_mr = (By.XPATH, "//input[@value='MR']")
    set_br = (By.XPATH, "//input[@value='BR']")

    # 아이콘
    icon_style = (By.XPATH, "//button[contains(text(),'스타일 선택')]")

    # 스타일
    corner_style = (By.XPATH, "//input[contains(@name,'antoine')]")

    # A/B/N 테스트 설정
    type_auto = (By.XPATH, "//input[@value='true']")
    target_order = (By.XPATH, "//input[@value='OR']")

    # 스케줄
    period_self = (By.XPATH, "//input[@value='MA']")
    period_set = (By.XPATH, "//input[@value='ET']")
    repeat_false = (By.XPATH, "//input[@value='false']")
    repeat_true = (By.XPATH, "//input[@value='true']")
    repeat_setting = (By.XPATH, "//button[contains(text(),'설정하기')]")
    repeat_setting_done = (By.XPATH, "//button[contains(text(),'확인')]")

    # 노출 옵션
    freq_combx = (By.XPATH, "//div[contains(text(),'매일 1번')]")
    freq_one = (By.XPATH, "//li[contains(text(),'1번')]")
    freq_month = (By.XPATH, "//li[contains(text(),'매월 1번')]")
    freq_week = (By.XPATH, "//li[contains(text(),'매주 1번')]")
    freq_day = (By.XPATH, "//li[contains(text(),'매일 1번')]")
    freq_session = (By.XPATH, "//li[contains(text(),'방문 세션마다')]")
    freq_page = (By.XPATH, "//li[contains(text(),'방문 페이지마다')]")
    freq_etc = (By.XPATH, "//li[contains(text(),'기타')]")
    priority_cb = (By.XPATH, "(//input[@type='checkbox'])[7]")

    # 완료
    cancelBtn = (By.XPATH, "//button[contains(text(),'취소')]")
    nextBtn = (By.XPATH, "//button[contains(text(),'다음 단계')]")
    saveBtn = (By.XPATH, "//button[contains(text(),'저장')]")

    # 몰 바로가기
    admin_icon = (By.XPATH, "/html[1]/body[1]/header[1]/div[1]/div[2]/button[2]")
    goto_mall = (By.XPATH, "//p[contains(text(),'몰 바로가기')]")

    # 서비스 페이지
    cam_popup = (By.XPATH, "(//img[@class='img_999999'])[1]")

    # 대시보드 (조회할 값 실제 작성)
    dashboard_onsite_ranking = (By.XPATH, "//h6[contains(text(),'[QA] PC/웹-페이지반복 테스트 캠페인')]")
    dashboard_onsite_impressions = (By.XPATH, "//h6[contains(text(),'노출 수')]/following-sibling::h6")
    dashboard_onsite_clicks = (By.XPATH, "//h6[contains(text(),'클릭 수')]/following-sibling::h6")
    dashboard_onsite_impressions_tab = (By.XPATH, "(//button[@role='tab'][contains(text(),'노출 수')])[1]")
    dashboard_onsite_clicks_tab = (By.XPATH, "(//button[@role='tab'][contains(text(),'클릭 수')])[1]")

    # -------------------------동작 선언 영역-------------------------
    # 만들기
    def click_create_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.createBtn, timeout).click()
    def click_create_btn_onsite(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.createBtn_onsite, timeout).click()
    def click_create_btn_inapp(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.createBtn_inapp, timeout).click()

    # 캠페인 입력
    def send_cam_name(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.cam_name, timeout)
        el.clear()
        el.send_keys(text)
    def send_cam_des(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.cam_des, timeout)
        el.clear()
        el.send_keys(text)

    # 접속 유형
    def click_type_pcweb(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.type_pcweb, timeout).click()
    def click_type_mobile(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.type_mobile, timeout).click()
    def click_type_mobile_web(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.type_mobile_web, timeout).click()
    def click_type_mobile_app(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.type_mobile_app, timeout).click()

    # 타겟 설정
    def click_seg_load(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_load, timeout).click()

    # 세그먼트 불러오기 RNB(설정할 값 실제 작성)
    def click_aiseg_tab(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.aiseg_tab, timeout).click()
    def click_seg_tab(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_tab, timeout).click()
    def click_now_pc_seg(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.now_pc_seg, timeout).click()
    def click_now_os_seg(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.now_os_seg, timeout).click()
    def click_select_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.selectBtn, timeout).click()

    # 추가
    def click_add_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.addBtn, timeout).click()
    def click_a_type(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.a_type, timeout).click()
    def click_b_type(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.b_type, timeout).click()
    def click_c_type(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.c_type, timeout).click()
    def click_d_type(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.d_type, timeout).click()
    def click_e_type(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.e_type, timeout).click()
    def click_type_del_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.type_del_icon, timeout).click()

    # 디자인 유형
    def click_design_popup(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.design_popup, timeout).click()
    def click_design_sticky_default(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.design_sticky_default, timeout).click()
    def click_design_sticky_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.design_sticky_btn, timeout).click()

    # URL 입력
    def send_input_url(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.input_url, timeout)
        el.clear()
        el.send_keys(text)
    def click_image_map(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.image_map, timeout).click()

    # 내용 입력
    def click_des_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.desBtn, timeout).click()
    def send_input_des(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.input_des, timeout)
        el.clear()
        el.send_keys(text)
    def click_sort_des(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.sort_des, timeout).click()
    def send_input_txt20(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.input_txt20, timeout)
        el.clear()
        el.send_keys(text)
    def send_input_txt16(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.input_txt16, timeout)
        el.clear()
        el.send_keys(text)
    def send_input_txt40(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.input_txt40, timeout)
        el.clear()
        el.send_keys(text)
    def send_input_txt15(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.input_txt15, timeout)
        el.clear()
        el.send_keys(text)
    def click_bold_cbx(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.bold_cbx, timeout).click()
    def click_bold_cbx2(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.bold_cbx2, timeout).click()
    def click_bold_cbx3(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.bold_cbx3, timeout).click()
    def click_sort_mid(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.sort_mid, timeout).click()
    def click_set_top(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.set_top, timeout).click()
    def click_set_bottom(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.set_bottom, timeout).click()

    # 노출 위치 설정
    def click_set_tl(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.set_tl, timeout).click()
    def click_set_ml(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.set_ml, timeout).click()
    def click_set_bl(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.set_bl, timeout).click()
    def click_set_tc(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.set_tc, timeout).click()
    def click_set_mc(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.set_mc, timeout).click()
    def click_set_bc(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.set_bc, timeout).click()
    def click_set_tr(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.set_tr, timeout).click()
    def click_set_mr(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.set_mr, timeout).click()
    def click_set_br(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.set_br, timeout).click()

    # 아이콘
    def click_icon_style(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.icon_style, timeout).click()

    # 스타일
    def click_corner_style(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.corner_style, timeout).click()

    # A/B/N 테스트 설정
    def click_type_auto(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.type_auto, timeout).click()
    def click_target_order(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.target_order, timeout).click()

    # 스케줄
    def click_period_self(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.period_self, timeout).click()
    def click_period_set(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.period_set, timeout).click()
    def click_repeat_false(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_false, timeout).click()
    def click_repeat_true(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_true, timeout).click()
    def click_repeat_setting(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_setting, timeout).click()
    def click_repeat_setting_done(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_setting_done, timeout).click()

    # 노출 옵션
    def click_freq_combx(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.freq_combx, timeout).click()
    def click_freq_one(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.freq_one, timeout).click()
    def click_freq_month(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.freq_month, timeout).click()
    def click_freq_week(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.freq_week, timeout).click()
    def click_freq_day(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.freq_day, timeout).click()
    def click_freq_session(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.freq_session, timeout).click()
    def click_freq_page(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.freq_page, timeout).click()
    def click_freq_etc(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.freq_etc, timeout).click()
    def click_priority_cb(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.priority_cb, timeout).click()

    # 완료
    def click_cancel_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.cancelBtn, timeout).click()
    def click_next_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.nextBtn, timeout).click()
    def click_save_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.saveBtn, timeout).click()

    # 몰 바로가기
    def click_admin_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.admin_icon, timeout).click()
    def click_goto_mall(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.goto_mall, timeout).click()

    # 서비스 페이지
    def click_cam_popup(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.cam_popup, timeout).click()

    # 대시 보드
    def is_ranking_campaign_displayed(self):
        try:
            return self.driver.find_element(*CampaignPage.dashboard_onsite_ranking).is_displayed()
        except NoSuchElementException:
            return False
    def get_onsite_impressions(self):
        import re
        elem = self.driver.find_element(*CampaignPage.dashboard_onsite_impressions)
        num = int(re.findall(r'\d+', elem.text)[0])
        return num
    def get_onsite_clicks(self):
        import re
        elem = self.driver.find_element(*CampaignPage.dashboard_onsite_clicks)
        num = int(re.findall(r'\d+', elem.text)[0])
        return num
    def click_dashboard_onsite_impressions_tab(self):
        return self.driver.find_element(*CampaignPage.dashboard_onsite_impressions_tab)
    def click_dashboard_onsite_clicks_tab(self):
        return self.driver.find_element(*CampaignPage.dashboard_onsite_clicks_tab)