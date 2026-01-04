
import time
from datetime import datetime

from setup.driver_setup import create_driver
from setup.config_loader import ConfigLoader

from actions.login_action import AdminLogin, EnterGelatto, ChatbotLogin
from actions.chatbot_action import ChatbotAction
from actions.gelatto_action import GelattoAction

from elements.chatbot_page import ChatbotService

from setup.logger import info, error 
import setup.selenium_utils as util
from selenium.webdriver.common.window import WindowTypes

class MainFlow:

    def __init__(self, driver, wait):

        self.driver = driver
        self.wait = wait
        # 페이지 객체 보관용
        self.gelatto = None
        self.chatbot = None
    
    def prepare_main(self):

        # Driver
        driver = self.driver
        wait = self.wait

        # Admin 
        admin_login = AdminLogin(driver, wait)
        admin_login.open_admin_page()
        admin_login.login_admin()
        admin_login.enter_shop()

        # Gelatto
        before = driver.window_handles[:]
        self.gelatto_tab_idx = 1
        self.gelatto = EnterGelatto(driver, wait, self.gelatto_tab_idx)
        self.gelatto.enter_gelatto()
        gelatto_handle = util.wait_new_tab(driver, before)
        self.driver.switch_to.window(gelatto_handle)
        self.gelatto.wait_gelatto_dash()
        time.sleep(2)
        self.gelatto_tab = gelatto_handle

        '''
        # 탭 추가 오픈
        before = driver.window_handles[:]
        self.driver.execute_script("window.open('');") # 새로운 탭 오픈
        time.sleep(2)
        blank_handle = util.wait_new_tab(driver, before)
        self.driver.switch_to.window(blank_handle)
        '''
        
        # 탭 추가 오픈 (JS 사용 ❌)
        self.driver.switch_to.new_window(WindowTypes.TAB)
        blank_handle = driver.current_window_handle
        driver.switch_to.window(blank_handle)

        # Shop (blank 탭에서 enter_chatbot 수행)
        handles = driver.window_handles[:]
        shop_tab_idx = -1
        shop_tab = handles[shop_tab_idx]
        shop = ChatbotLogin(driver, wait, shop_tab, shop_tab_idx)
        shop.enter_chatbot()
        time.sleep(3)

        # Chatbot
        handles = driver.window_handles
        self.chatbot_tab_idx = 3
        self.chatbot_tab = handles[self.chatbot_tab_idx]
        self.chatbot = ChatbotService(driver, wait, self.chatbot_tab)
        self.chatbot.switch_tab()
        time.sleep(3)

class ChatbotFlow:

    def __init__(self, driver, wait, tab):
        self.driver = driver
        self.wait = wait
        self.tab = tab
        self.chatbot = ChatbotAction(driver, wait, tab)
    
    # 보낸 메세지, 응답 받은 메세지 
    def test_chatbot(self):
        sent_txt, reply_txt = self.chatbot.chatbot_circle()
        return sent_txt, reply_txt
    
    def repeat_chatbot_circle(self, count=25):
        for i in range(1, count+1):
            print(f"[Chatbot] Iteration {i}/{count}")
            info(f"[Chatbot] Iteration {i}/{count}")
            self.chatbot.chatbot_circle()


class GelattoFlow:

    def __init__(self, driver, wait, tab):
        self.driver = driver
        self.wait = wait
        self.tab = tab
        self.gelatto = GelattoAction(driver, wait, tab)

    # 봇 분석 정보 세개
    def get_bot_info(self):
        return self.gelatto.get_3_cnt()


if __name__ == "__main__":
    driver, wait = create_driver()

    main_flow = MainFlow(driver, wait)
    main_flow.prepare_main()
    chat_flow = ChatbotFlow(driver, wait, main_flow.chatbot_tab)
    gelatto = GelattoAction(driver, wait, main_flow.gelatto_tab)

    # 챗봇 전송 확인
    gelatto.make_gelatto()
    old_credit = int(gelatto.get_credit_cnt())
    sent_txt, reply_txt = chat_flow.test_chatbot()
    print(sent_txt, reply_txt)
    
    #챗봇 메세지 반복 전송
    chat_flow.repeat_chatbot_circle()
    new_credit = int(gelatto.get_credit_cnt())

    history_time, usr_msg = gelatto.get_msg_info()
    print(history_time, usr_msg)

    if new_credit-1 == old_credit:
        info("크레딧 수치 변화 OK")
        print("크레딧 수치 변화 OK")
    else:
        error("크레딧 수치 변화 NG")
        print("크레딧 수치 변화 NG")
        
    gelatto.register_topic()
    gelatto.register_word()