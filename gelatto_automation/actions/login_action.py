
import time
import os 

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from setup.config_loader import ConfigLoader
from elements.login_page import LoginPage

from setup.logger import info

class AdminLogin:

    def __init__(self, driver, wait):
        # 1. 드라이버 기본 설정
        self.driver = driver
        self.wait = wait
        # 1. 설정 파일 로드
        self.config = ConfigLoader()
        # 2. 페이지 객체 주입
        self.login_page = LoginPage(driver)

    def switch_tab(self):
        self.driver.switch_to.window(self.tab)

    def open_admin_page(self):
        ### yaml 파일에서 admin_page URL 불러오기
        admin_url = self.config.admin_url
        self.driver.get(admin_url)

    def login_admin(self):
        ### admin 페이지 로그인
        username = self.config.username
        password = self.config.password
        # 아이디 입력
        self.wait.until(EC.presence_of_element_located(self.login_page.input_id))
        self.login_page.send_id().send_keys(username)
        # 비밀번호 입력
        self.login_page.send_pw().send_keys(password)
        # 로그인 버튼 클릭
        self.login_page.click_login_btn().click()
        
        info("Admin Login Success!")
        print("Admin Login Success!")
        time.sleep(3)
    
    def enter_shop(self):
        # shop 검색
        info("shop 검색")
        shop = self.config.get_shop
        self.login_page.search_shop().send_keys(shop)
        time.sleep(1)
        # shop 선택
        info("shop 선택")
        self.login_page.click_shop_login_btn().click()
        # 대시보드 메뉴 노출까지 대기
        self.wait.until(
            EC.visibility_of_element_located(self.login_page.dashboardMenu)
        )
        info("대시보드 노출")
        print("대시보드 노출")
        time.sleep(1)


class EnterGelatto:

    # -------------------------element 선언 영역-------------------------
    # GNB 드롭다운 버튼
    gnb_dropdown = (By.XPATH, "/html/body/header/div/div[1]/button[2]")
    # gelatto 요소
    gelatto_elem = (By.XPATH, "//div[contains(text(),'gelatto')]")

    # -------------------------함수 선언 영역-------------------------

    def __init__(self, driver, wait, target_tab_idx):
        self.driver = driver
        self.wait = wait
        self.target_tab_idx = target_tab_idx

    def switch_tab(self):
        self.driver.switch_to.window(self.tab)

    def open_gnb_menu(self):
        self.wait.until(EC.element_to_be_clickable(self.gnb_dropdown)).click()

    def click_gelatto(self):
        self.wait.until(EC.element_to_be_clickable(self.gelatto_elem)).click()

    def switch_to_tab(self):
        tabs = self.driver.window_handles
        self.driver.switch_to.window(tabs[self.target_tab_idx])
        print(f"Switched to tab index: {self.target_tab_idx}")

    def enter_gelatto(self):
        self.open_gnb_menu()
        self.click_gelatto()
        time.sleep(3)
        info("Gelatto Page Loaded!")
        print("Gelatto Page Loaded!")


class ChatbotLogin:

    # -------------------------element 선언 영역-------------------------
    # 젤라또 챗봇
    chatbot_btn = (By.XPATH, '//*[@id="gelattoUIButton"]')

    # -------------------------함수 선언 영역-------------------------
    
    def __init__(self, driver, wait, tab, target_tab_idx):
        self.driver = driver
        self.wait = wait
        self.config = ConfigLoader()
        self.tab = tab
        self.tab_idx = target_tab_idx
    
    def switch_tab(self):
        self.driver.switch_to.window(self.tab)
        time.sleep(2)
    
    def open_shop_page(self):
        self.switch_tab()
        ### yaml 파일에서 shop_page URL 불러오기
        shop_url = self.config.shop_url
        self.driver.get(shop_url)
        time.sleep(3)
    
    def click_chatbot(self):
        self.driver.find_element(*self.chatbot_btn).click()
        time.sleep(1)

    def switch_to_tab(self):
        tabs = self.driver.window_handles
        self.driver.switch_to.window(tabs[self.tab_idx])
        print(f"Switched to tab index: {self.tab_idx}")

    def enter_chatbot(self):
        self.open_shop_page()
        self.click_chatbot()
        self.switch_to_tab()
        time.sleep(3)
        info("Shop Chatbot Loaded!")
        print("Shop Chatbot Loaded!")


