from selenium.webdriver.common.by import By

from PageObjects.GroobeeActions import GroobeeActions
from utilities.BaseClass import BaseClass

class RecommendPage(GroobeeActions):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    # -------------------------element 선언 영역-------------------------
    # 만들기
    createBtn = (By.XPATH, "//button[contains(text(),'만들기')]")

    # 캠페인 입력
    cam_title = (By.XPATH, "//h1[contains(text(),'새로운 AI 상품 추천 캠페인 만들기')]")
    cam_name = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 40자']")
    cam_des = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 400자']")

    # 접속 유형
    type_pcweb = (By.XPATH, "//input[@value='PC']")
    type_mobile = (By.XPATH, "//input[@value='MO']")
    type_mobile_web = (By.XPATH, "//input[@value='MW']")
    type_mobile_app = (By.XPATH, "//input[@value='MA']")

    # 노출 페이지
    page_select_cb = (By.XPATH, "//div[@role='combobox']")
    page_select_cb_main = (By.XPATH, "//li[contains(text(),'메인')]")
    page_select_cb_category = (By.XPATH, "//li[contains(text(),'카테고리')]")
    page_select_cb_product = (By.XPATH, "//li[contains(text(),'상품 상세')]")
    page_select_cb_cart = (By.XPATH, "//li[contains(text(),'장바구니')]")
    page_select_cb_search = (By.XPATH, "//li[contains(text(),'검색 결과')]")
    page_select_cb_input = (By.XPATH, "//li[contains(text(),'직접 입력')]")
    page_select_cb_input_bx = (By.XPATH, "//input[@id='downshift-multiple-input']")
    page_select_cb_all = (By.XPATH, "//li[contains(text(),'모든 페이지')]")

    # 알고리즘 설정
    set_algo_goods = (By.XPATH, "//input[@value='GD']")
    set_algo_special = (By.XPATH, "//input[@value='PL']")
    goods_all_cb = (By.XPATH, "(//input[@type='checkbox'])[1]")
    visitors_all_cb = (By.XPATH, "(//input[@type='checkbox'])[11]")
    stat_all_cb = (By.XPATH, "(//input[@type='checkbox'])[18]")

    # 최적화 목표
    target_click = (By.XPATH, "//input[@value='CL']")
    target_order = (By.XPATH, "//input[@value='OR']")

    # 타겟 설정
    target_set = (By.XPATH, "//h6[contains(text(),'타겟 설정')]")
    seg_load = (By.XPATH, "//button[contains(text(),'세그먼트 불러오기')]")

    # 세그먼트 불러오기
    aiseg_tab = (By.XPATH, "//button[@id='basic-tab-0']")
    seg_tab = (By.XPATH, "//button[@id='basic-tab-1']")
    purchase_self_seg = (By.XPATH, "//h6[contains(text(),'[QA] 직접 입력 테스트 세그먼트')]")
    selectBtn = (By.XPATH, "//button[contains(text(),'선택')]")

    # 디자인 유형
    design_script = (By.XPATH, "//input[@value='JS']")
    design_data = (By.XPATH, "//input[@value='CU']")

    # 필터링 설정
    filter_click = (By.XPATH, "(//input[@type='checkbox'])[1]")
    filter_order = (By.XPATH, "(//input[@type='checkbox'])[2]")

    # 스케줄
    schedule_self = (By.XPATH, "//input[@value='MA']")
    schedule_enter = (By.XPATH, "//input[@value='ET']")

    # 완료
    cancelBtn = (By.XPATH, "//button[contains(text(),'취소')]")
    nextBtn = (By.XPATH, "//button[contains(text(),'다음 단계')]")
    saveBtn = (By.XPATH, "//button[contains(text(),'저장')]")

    # -------------------------동작 선언 영역-------------------------
    # 만들기
    def click_create_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.createBtn, timeout).click()

    # 캠페인 입력
    def send_cam_name(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.cam_name, timeout).click()
    def send_cam_des(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.cam_des, timeout).click()

    # 접속 유형
    def click_type_pcweb(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.type_pcweb, timeout).click()
    def click_type_mobile(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.type_mobile, timeout).click()
    def click_type_mobile_web(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.type_mobile_web, timeout).click()
    def click_type_mobile_app(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.type_mobile_app, timeout).click()

    # 노출 페이지
    def click_page_select_cb(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.page_select_cb, timeout).click()
    def click_page_select_cb_main(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.page_select_cb_main, timeout).click()
    def click_page_select_cb_category(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.page_select_cb_category, timeout).click()
    def click_page_select_cb_product(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.page_select_cb_product, timeout).click()
    def click_page_select_cb_cart(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.page_select_cb_cart, timeout).click()
    def click_page_select_cb_search(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.page_select_cb_search, timeout).click()
    def click_page_select_cb_input(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.page_select_cb_input, timeout).click()
    def send_page_select_cb_input_bx(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.page_select_cb_input_bx, timeout).click()
    def click_page_select_cb_all(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.page_select_cb_all, timeout).click()

    # 알고리즘 설정
    def click_set_algo_goods(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.set_algo_goods, timeout).click()
    def click_set_algo_special(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.set_algo_special, timeout).click()
    def click_goods_all_cb(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.goods_all_cb, timeout).click()
    def click_visitors_all_cb(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.visitors_all_cb, timeout).click()
    def click_stat_all_cb(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.stat_all_cb, timeout).click()

    # 최적화 목표
    def click_target_click(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.target_click, timeout).click()
    def click_target_order(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.target_order, timeout).click()

    # 타겟 설정
    def click_target_set(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.target_set, timeout).click()
    def click_seg_load(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_load, timeout).click()

    # 세그먼트 불러오기 RNB(설정할 값 실제 작성)
    def click_aiseg_tab(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.aiseg_tab, timeout).click()
    def click_seg_tab(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_tab, timeout).click()
    def click_purchase_self_seg(self, timeout=10):
        return self.driver.find_elements(*RecommendPage.purchase_self_seg, timeout).click()
    def click_select_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.selectBtn, timeout).click()

    # 디자인 유형
    def click_design_script(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.design_script, timeout).click()
    def click_design_data(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.design_data, timeout).click()

    # 필터링 설정
    def click_filter_click(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.filter_click, timeout).click()
    def click_filter_order(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.filter_order, timeout).click()

    # 스케줄
    def click_schedule_self(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.schedule_self, timeout).click()
    def click_schedule_enter(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.schedule_enter, timeout).click()

    # 완료
    def click_cancel_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.cancelBtn, timeout).click()
    def click_next_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.nextBtn, timeout).click()
    def click_save_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.saveBtn, timeout).click()