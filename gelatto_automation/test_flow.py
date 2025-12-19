
import time
from datetime import datetime

from setup.driver_setup import create_driver
from actions.login_action import AdminLogin, EnterGelatto, ChatbotLogin
from elements.chatbot_page import ChatbotService
from actions.chatbot_action import ChatbotAction
from actions.gelatto_action import GelattoAction

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
        self.gelatto_tab_idx = 1   # 두번째 탭
        self.gelatto = EnterGelatto(driver, wait, self.gelatto_tab_idx)
        self.gelatto.enter_gelatto()
        time.sleep(2)

        # 탭 추가 오픈
        driver.execute_script("window.open('');") # 새로운 탭 오픈
        time.sleep(2)

        # 열린 탭 모두 확인하여 인덱스 부여
        handles = driver.window_handles
        self.gelatto_tab = handles[self.gelatto_tab_idx]

        # Shop
        handles = driver.window_handles
        shop_tab_idx = 2
        shop_tab = handles[shop_tab_idx]
        shop = ChatbotLogin(driver, wait, shop_tab, shop_tab_idx)
        shop.enter_chatbot()
        time.sleep(2)

        # Chatbot
        handles = driver.window_handles
        self.chatbot_tab_idx = 3
        self.chatbot_tab = handles[self.chatbot_tab_idx]
        self.chatbot = ChatbotService(driver, wait, self.chatbot_tab)
        self.chatbot.switch_tab()
        time.sleep(2)

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

    gelatto.make_gelatto()
    sent_txt, reply_txt = chat_flow.test_chatbot()
    print(sent_txt, reply_txt)

    history_time, usr_msg = gelatto.get_msg_info()
    print(history_time, usr_msg)

    if sent_txt == usr_msg:
        print("chatbot message OK")
    else:
        print("chatbot message NG")

    gelatto.register_topic()
    gelatto.register_word()