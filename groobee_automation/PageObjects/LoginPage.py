

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:

    def __init__(self, driver):
        self.driver = driver

    #-------------------------element 선언 영역-------------------------
    #로그인
    input_id = (By.XPATH, "//input[@id='outlined-id']")
    input_pw = (By.XPATH, "//input[@id='outlined-adornment-password']")
    loginBtn = (By.XPATH, "//button[contains(text(),'로그인')]")

    #고객사 검색
    search_box = (By.XPATH, "//input[@placeholder='전체 통합 검색']")
    shop_loginBtn = (By.XPATH, "//button[contains(text(),'로그인')]")

    #대시보드
    dashboardMenu = (By.XPATH, "//p[contains(text(),'대시보드')]")

    #-------------------------동작 선언 영역-------------------------
    #로그인
    def send_id(self):
        return self.driver.find_element(*self.input_id)
    def send_pw(self):
        return self.driver.find_element(*self.input_pw)
    def click_login_btn(self):
        self.driver.find_element(*self.loginBtn).click()

    #고객사 검색
    def search_shop(self):
        return self.driver.find_element(*self.search_box).send_keys("groobeeshop")
    def click_shop_login_btn(self):
        self.driver.find_element(*self.shop_loginBtn).click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(self.dashboardMenu))