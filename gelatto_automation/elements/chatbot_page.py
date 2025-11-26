
import os
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

class ChatbotService:

    def __init__(self, driver, wait, tab):
        self.driver = driver
        self.wait = wait
        self.tab = tab
    
    # -------------------------element 선언 영역-------------------------
    # MAIN
    ## 대화 입력 창
    text_input_elem = (By.XPATH, '//*[@id="chatTextArea"]')
    ## 전송 버튼
    send_msg_btn = (By.XPATH, "/html/body/div[1]/div[2]/div/div[2]/div/div/form/button")
    ## 답변 영역
    bot_reply_elem = (By.XPATH, "/html/body/div[1]/div[2]/div/div[1]/div[3]")
    
    # GNB
    ## 새로운 대화 버튼
    new_chat_btn = (By.XPATH, "/html/body/div[1]/div[1]/div/header/button/span[1]")

    # -------------------------동작 선언 영역-------------------------

    def switch_tab(self):
        self.driver.switch_to.window(self.tab)
        time.sleep(1.5)

    # 새로운 대화 생성
    def create_new(self):
        self.switch_tab()
        self.driver.wait.until(EC.element_to_be_clickable(*self.new_chat_btn)).click()
        time.sleep(2)

    def send_message(self, date_time):
        self.switch_tab()
        time.sleep(0.7)
        # 채팅텍스트박스 진입
        text_input_box = self.driver.find_element(*self.text_input_elem)
        text_input_box.click()
        time.sleep(2)
        # 메세지 입력
        message = f'[AUTO] QA Test {date_time}'
        text_input_box.send_keys(message)
        time.sleep(1)
        # 엔터키 입력
        text_input_box.send_keys(Keys.ENTER)
        print("Sned Mesage Success!")
        return message

    def get_reply_msg(self):
        self.switch_tab()
        reply_txt = self.driver.find_element(*self.bot_reply_elem).text
        return reply_txt


