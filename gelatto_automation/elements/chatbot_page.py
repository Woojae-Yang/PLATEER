
import os
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from setup.base_action import BaseAction
import setup.selenium_utils as util
from setup.logger import info

class ChatbotService(BaseAction):

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
        info("새로운 대화 생성")
        self.wait_and_click(EC.element_to_be_clickable, self.new_chat_btn, "새로운 대화")
        time.sleep(2)

    def send_message(self, date_time):
        self.switch_tab()
        time.sleep(0.7)
        # 채팅텍스트박스 진입
        info("채팅 텍스트박스 진입")
        text_input_box = self.find(self.text_input_elem, "채팅 입력 텍스트박스")
        text_input_box.click()
        time.sleep(2)
        # 메세지 입력
        info("메세지 입력")
        message = f'[AUTO] QA Test {date_time}'
        text_input_box.send_keys(message)
        time.sleep(1)
        # 엔터키 입력
        info("메세지 전송")
        text_input_box.send_keys(Keys.ENTER)
        print("Sned Mesage Success!")
        info("Sned Mesage Success!")
        return message

    def get_reply_msg(self):
        self.switch_tab()
        reply_txt = self.find(self.bot_reply_elem, "챗봇 응답 메세지").text
        return reply_txt


