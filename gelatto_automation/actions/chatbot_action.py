
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from elements.chatbot_page import ChatbotService

class ChatbotAction:
    
    def __init__(self, driver, wait, tab):
        self.driver = driver
        self.wait = wait
        self.tab = tab
        self.chatbot = ChatbotService(driver, wait, tab)

    # 챗봇 > 새로운 대화 > 대화창 입력 > 전송 버튼 (Keys.ENTER) > 응답 메세지 추출
    def chatbot_circle(self):
        self.chatbot.switch_tab()
        time.sleep(0.5)

        self.driver.refresh()
        time.sleep(0.5)

        #메세지 전송
        now = datetime.now()
        now_date = now.strftime('%Y.%m.%d')
        now_time = now.strftime('%H:%M:%S')
        self.input_time = f'{now_date} {now_time}'
        
        # 전송된 메세지
        sent_txt = self.chatbot.send_message(self.input_time)
        time.sleep(5)
        
        # 응답 메세지
        reply_txt = self.chatbot.get_reply_msg()
        return sent_txt, reply_txt