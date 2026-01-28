from selenium.webdriver.common.by import By
from utilities.BaseClass import BaseClass

class LoginPage:

    def __init__(self, driver):
        self.driver = driver

    # ------------------------------ element 선언 ------------------------------
    # 로그인
    input_id = (By.XPATH, "//input[@id='outlined-id']")
    input_pw = (By.XPATH, "//input[@id='outlined-adornment-password']")
    loginBtn = (By.XPATH, "//button[contains(text(),'로그인')]")

    # 고객사 검색
    search_box = (By.XPATH, "//input[@placeholder='전체 통합 검색']")
    shop_loginBtn = (By.XPATH, "//button[contains(text(),'로그인')]")

    # 대시보드 메뉴
    dashboardMenu = (By.XPATH, "//p[contains(text(),'대시보드')]")

    # ------------------------------ action + wait ------------------------------
    # 로그인
    def send_id(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.input_id, timeout)
        el.clear()
        el.send_keys(text)
    def send_pw(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.input_pw, timeout)
        el.clear()
        el.send_keys(text)
    def click_login(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.loginBtn, timeout).click()

    # 고객사 검색
    def search_shop(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.search_box, timeout)
        el.clear()
        el.send_keys(text)
    def click_shop_login(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.shop_loginBtn, timeout).click()

    # 대시보드 메뉴
    def wait_dashboard_loaded(self, timeout=10):
        BaseClass.wait_visible(self.driver, self.dashboardMenu, timeout)
        return True