from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PageObjects.GroobeeActions import GroobeeActions
from utilities.BaseClass import BaseClass

class AisegmentPage(GroobeeActions):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    # -------------------------element 선언 영역-------------------------
    # 만들기
    createBtn = (By.XPATH, "//button[contains(text(),'만들기')]")
    rfm_seg = (By.XPATH, "//li[contains(text(),'RFM 세그먼트')]")
    purchase_seg = (By.XPATH, "//li[contains(text(),'구매 확률 세그먼트')]")
    tastes_seg = (By.XPATH, "//li[contains(text(),'취향 분석 세그먼트')]")

    # RFM 세그먼트
    rfm_seg_title = (By.XPATH, "//h1[contains(text(),'새로운 RFM 세그먼트 만들기')]")
    rfm_seg_name = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 40자']")
    rfm_seg_des = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 400자']")

    # RFM 세그먼트 선택
    seg_vip = (By.XPATH, "//h6[normalize-space()='VIP']")
    seg_rare = (By.XPATH, "//h6[contains(text(),'뜸한 VIP')]")
    seg_poten = (By.XPATH, "//h6[contains(text(),'잠재 VIP')]")
    seg_new = (By.XPATH, "//h6[contains(text(),'신규 고객')]")
    seg_now = (By.XPATH, "//h6[contains(text(),'지금 잡아야 할 고객')]")
    seg_care = (By.XPATH, "//h6[contains(text(),'신경써야 할 고객')]")
    seg_worry = (By.XPATH, "//h6[contains(text(),'이탈 우려')]")
    seg_left_vip = (By.XPATH, "//h6[contains(text(),'이탈한 VIP')]")
    seg_left_poten_vip = (By.XPATH, "//h6[contains(text(),'이탈한 잠재 VIP')]")
    seg_left = (By.XPATH, "//h6[contains(text(),'이탈한 고객')]")

    # 구매 확률 세그먼트
    purchase_seg_title = (By.XPATH, "//h1[contains(text(),'새로운 구매 확률 세그먼트 만들기')]")
    purchase_seg_name = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 40자']")
    purchase_seg_des = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 400자']")

    # 구매 확률 세그먼트 선택
    purchase_combo = (By.XPATH, "//div[@role='combobox']")
    purchase_20 = (By.XPATH, "//li[normalize-space()='0~20%']")
    purchase_40 = (By.XPATH, "//li[normalize-space()='21~40%']")
    purchase_60 = (By.XPATH, "//li[normalize-space()='41~60%']")
    purchase_80 = (By.XPATH, "//li[normalize-space()='61~80%']")
    purchase_100 = (By.XPATH, "//li[normalize-space()='81~100%']")
    purchase_self = (By.XPATH, "//li[contains(text(),'직접 입력')]")
    purchase_min = (By.XPATH, "//div[contains(@class,'MuiStack-root')]//input[@type='text'][1]")
    purchase_max = (By.XPATH, "//div[contains(@class,'MuiStack-root')]//input[@type='text'][2]")
    checkBtn = (By.XPATH, "//button[contains(text(),'확인하기')]")

    # 취향 분석 세그먼트
    tastes_seg_title = (By.XPATH, "//h1[contains(text(),'새로운 취향 분석 세그먼트 만들기')]")
    tastes_seg_name = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 40자']")
    tastes_seg_des = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 400자']")

    # 취향 분석 세그먼트 선택
    tastes_seg_main = (By.XPATH, "//button[contains(text(),'대표 상품')]")
    tastes_seg_view = (By.XPATH, "//button[contains(text(),'많이 조회한 상품')]")
    tastes_handmade = (By.XPATH, "//h6[contains(text(),'핸드메이드 코트')]")

    # 완료
    cancelBtn = (By.XPATH, "//button[contains(text(),'취소')]")
    saveBtn = (By.XPATH, "//button[contains(text(),'저장')]")

    # -------------------------동작 선언 영역-------------------------
    # 만들기
    def click_create_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.createBtn, timeout).click()
    def click_rfm_seg(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.rfm_seg, timeout).click()
    def click_purchase_seg(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.purchase_seg, timeout).click()
    def click_tastes_seg(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.tastes_seg, timeout).click()

    # RFM 세그먼트 입력
    def send_rfm_seg_name(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.rfm_seg_name, timeout)
        el.clear()
        el.send_keys(text)
    def send_rfm_seg_des(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.rfm_seg_des, timeout)
        el.clear()
        el.send_keys(text)

    # RFM 세그먼트 선택 옵션을 dict 형태로 반환
    def get_rfm_options(self):
        return {
            "VIP": self.driver.find_element(*AisegmentPage.seg_vip),
            "뜸한 VIP": self.driver.find_element(*AisegmentPage.seg_rare),
            "잠재 VIP": self.driver.find_element(*AisegmentPage.seg_poten),
            "신규 고객": self.driver.find_element(*AisegmentPage.seg_new),
            "지금 잡아야 할 고객": self.driver.find_element(*AisegmentPage.seg_now),
            "신경써야 할 고객": self.driver.find_element(*AisegmentPage.seg_care),
            "이탈 우려": self.driver.find_element(*AisegmentPage.seg_worry),
            "이탈한 VIP": self.driver.find_element(*AisegmentPage.seg_left_vip),
            "이탈한 잠재 VIP": self.driver.find_element(*AisegmentPage.seg_left_poten_vip),
            "이탈한 고객": self.driver.find_element(*AisegmentPage.seg_left),
        }

    # 구매 확률 세그먼트 입력
    def send_purchase_seg_name(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.purchase_seg_name, timeout)
        el.clear()
        el.send_keys(text)
    def send_purchase_seg_des(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.purchase_seg_des, timeout)
        el.clear()
        el.send_keys(text)
    def send_purchase_seg_min(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.purchase_min, timeout)
        el.clear()
        el.send_keys(text)
    def send_purchase_seg_max(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.purchase_max, timeout)
        el.clear()
        el.send_keys(text)
    def click_check_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.checkBtn, timeout).click()

    # 구매 확률 세그먼트 선택
    def click_purchase_combo(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.purchase_combo, timeout).click()

    # 구매 확률 세그먼트 선택 옵션을 dict 형태로 반환
    def get_purchase_options(self):
        self.click_purchase_combo()

        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located(AisegmentPage.purchase_20)
        )

        options = {
            "0~20%": self.driver.find_element(*AisegmentPage.purchase_20),
            "21~40%": self.driver.find_element(*AisegmentPage.purchase_40),
            "41~60%": self.driver.find_element(*AisegmentPage.purchase_60),
            "61~80%": self.driver.find_element(*AisegmentPage.purchase_80),
            "81~100%": self.driver.find_element(*AisegmentPage.purchase_100),
            "직접 입력": self.driver.find_element(*AisegmentPage.purchase_self),
        }

        # 스크롤 후 읽기
        for opt in options.values():
            self.driver.execute_script("arguments[0].scrollIntoView(true);", opt)

        # 콤보 박스 닫기
        self.driver.find_element(*AisegmentPage.purchase_20).click()
        return options

    # 취향 분석 세그먼트 입력
    def send_tastes_seg_name(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.tastes_seg_name, timeout)
        el.clear()
        el.send_keys(text)
    def send_tastes_seg_des(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.tastes_seg_des, timeout)
        el.clear()
        el.send_keys(text)

    # 취향 분석 세그먼트 선택
    def click_tastes_seg_main(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.tastes_seg_main, timeout).click()
    def click_tastes_seg_view(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.tastes_seg_view, timeout).click()
    def click_tastes_handmade(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.tastes_handmade, timeout).click()

    # 완료
    def click_cancel_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.cancelBtn, timeout).click()
    def click_save_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.saveBtn, timeout).click()

    # 생성된 세그먼트 리스트
    def get_seg_list_item(self, seg_name):
        return self.driver.find_element(By.XPATH, f"//p[contains(text(), '{seg_name}')]")