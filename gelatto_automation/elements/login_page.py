
from selenium.webdriver.common.by import By

from setup.base_action import BaseAction
import setup.selenium_utils as util
from setup.logger import info

class LoginPage(BaseAction):

    def __init__(self, driver):
        self.driver = driver

    # -------------------------element 선언 영역-------------------------
    # 로그인
    input_id = (By.XPATH, "//input[@id='outlined-id']")
    input_pwd = (By.XPATH, "//input[@id='outlined-adornment-password']")
    loginBtn = (By.XPATH, "//button[contains(text(),'로그인')]")

    # 고객사 검색
    search_box = (By.XPATH, "//input[@placeholder='전체 통합 검색']")
    shop_loginBtn = (By.XPATH, "//button[contains(text(),'로그인')]")

    # 대시보드 메뉴
    dashboardMenu = (By.XPATH, "//p[contains(text(),'대시보드')]")

    # -------------------------동작 선언 영역-------------------------
    # 로그인
    def send_id(self):
        return self.find(self.input_id, "로그인 ID")
    def send_pw(self):
        return self.find(self.input_pw, "로그인 PW")
    def click_login_btn(self):
        return self.find(self.loginBtn, "로그인 버튼")

    # 고객사 검색
    def search_shop(self):
        return self.find(self.search_box, "shop 검색")
    def click_shop_login_btn(self):
        return self.find(self.shop_loginBtn, "shop 로그인")