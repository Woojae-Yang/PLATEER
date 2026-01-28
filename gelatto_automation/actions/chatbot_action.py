
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from elements.chatbot_page import ChatbotService

from setup.logger import info, error 

class ChatbotAction:
    
    def __init__(self, driver, wait, tab):
        self.driver = driver
        self.wait = wait
        self.tab = tab
        self.chatbot = ChatbotService(driver, wait, tab)

    # 챗봇 > 새로운 대화 > 대화창 입력 > 전송 버튼 (Keys.ENTER) > 응답 메세지 추출
    def chatbot_circle(self):
        self.chatbot.switch_tab()
        info(f"[Chatbot] after switch: handle={self.driver.current_window_handle}")
        info(f"[Chatbot] after switch: url={self.driver.current_url}")
        info(f"[Chatbot] after switch: title={self.driver.title}")
        time.sleep(2)

        #메세지 전송
        now = datetime.now()
        now_date = now.strftime('%Y.%m.%d')
        now_time = now.strftime('%H:%M:%S')
        self.input_time = f'{now_date} {now_time}'
        
        # 전송된 메세지
        sent_txt = self.chatbot.send_message(self.input_time)
        time.sleep(8)
        
        # 응답 메세지
        reply_txt = self.chatbot.get_reply_msg()
        return sent_txt, reply_txt

    def get_chatbot_txt(self):
        self.chatbot.switch_tab()
        info(f"[Chatbot] after switch: handle={self.driver.current_window_handle}")
        info(f"[Chatbot] after switch: url={self.driver.current_url}")
        info(f"[Chatbot] after switch: title={self.driver.title}")
        self.driver.refresh()
        time.sleep(2)

        # 대표 문구
        self.wait.until(EC.presence_of_element_located(self.chatbot.welcome_h1))
        welcome_h1_txt = self.driver.find_element(*self.chatbot.welcome_h1).text
        
        # 첫인사
        welcome_hello_txt = self.driver.find_element(*self.chatbot.welcome_hello).text
        
        # 플레이스홀더
        self.wait.until(EC.visibility_of_element_located(self.chatbot.text_input_elem))
        chatbot_placeholder_txt = self.driver.find_element(*self.chatbot.text_input_elem).get_attribute("placeholder")
            
        return welcome_h1_txt, welcome_hello_txt, chatbot_placeholder_txt

