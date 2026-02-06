from selenium.webdriver.common.by import By
from PageObjects.GroobeeActions import GroobeeActions
from utilities.BaseClass import BaseClass

class SegmentPage(GroobeeActions):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    # ------------------------------ element 선언 ------------------------------
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
    rnb_system_os = (By.XPATH, "//h6[contains(text(), '접속 OS')]")
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
    seg_setting1_android = (By.XPATH, "//li[normalize-space()='Android']")
    seg_setting2 = (By.XPATH, "(//div[contains(@role,'combobox')])[2]")
    seg_setting2_yes = (By.XPATH, "//li[contains(text(),'일 때')]")
    seg_setting3 = (By.XPATH, "(//div[contains(@role,'combobox')])[3]")
    seg_setting3_ios = (By.XPATH, "//li[normalize-space()='iOS']")
    seg_setting4 = (By.XPATH, "(//div[contains(@role,'combobox')])[4]")
    seg_setting4_yes = (By.XPATH, "//li[contains(text(),'일 때')]")
    seg_setting_or = (By.XPATH, "//button[normalize-space()='OR']")
    seg_setting_and = (By.XPATH, "//button[normalize-space()='AND']")

    # ------------------------------ action + wait ------------------------------
    # 세그먼트 입력
    def send_seg_name(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.seg_name, timeout)
        el.clear()
        el.send_keys(text)
    def send_seg_des(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.seg_des, timeout)
        el.clear()
        el.send_keys(text)

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
    def click_rnb_cart_act(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_cart_act, timeout).click()
    def click_rnb_order_act(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_order_act, timeout).click()
    def click_rnb_custom(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_custom, timeout).click()
    def click_rnb_choose(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rnb_choose, timeout).click()

    # 세그먼트 변수 설정(설정할 값 실제 작성)
    def click_seg_setting1(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_setting1, timeout).click()
    def click_seg_setting1_pc(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_setting1_pc, timeout).click()
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