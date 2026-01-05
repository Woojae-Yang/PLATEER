
import os
import time

from elements.gelatto_page import GelattoProduct
from setup.config_loader import ConfigLoader

from setup.logger import info

class GelattoAction:

    def __init__(self, driver, wait, tab):
        self.driver = driver
        self.wait = wait
        self.tab = tab
        self.gelatto = GelattoProduct(driver, wait, tab)
        self.config = ConfigLoader()

    # 분석 리포트 > `봇 분석` 탭 > 수치 세개 추출
    def get_3_cnt(self):
        info("[봇 분석]탭에서 수치 추출하기")
        # 챗봇 응답 대화 수
        conv_cnt = self.gelatto.get_conversation_cnt().split()[0]
        # 챗봇 응답 메세지 수
        msg_cnt = self.gelatto.get_msg_cnt()
        # 평균 응답 메세지 수
        avg_msg_cnt = self.gelatto.get_avg_cnt()
        return conv_cnt, msg_cnt, avg_msg_cnt
    
    # 젤라또 만들기
    def make_gelatto(self):
        self.gelatto.switch_tab()
        time.sleep(3)
        self.gelatto.driver.save_screenshot("./logs/ebug.png")
        info("젤라또 만들기")
        # 젤라또 만들기 진입
        info(f"[DEBUG-before] url={self.driver.current_url} handles={self.driver.window_handles}")
        self.gelatto.enter_make_gelatto()
        info(f"[DEBUG-after] url={self.driver.current_url} handles={self.driver.window_handles}")
        self.gelatto.click_setting_tab()
        self.gelatto.input_values()
        self.gelatto.click_save()
        

    # 분석 리포트 > `봇 내역` 탭 > 데이터 테이블 > 내역 일시, 사용자 메세지
    def get_msg_info(self):
        info("[봇 내역]탭에서 데이터 추출하기")
        self.gelatto.switch_tab()
        time.sleep(3)
        # 분석 리포트 진입
        self.gelatto.enter_report()
        # 봇 내역 탭 진입
        self.gelatto.enter_bot_history()
        # 내역 일시
        history_time = self.gelatto.get_history_date()
        # 사용자 메세지
        usr_msg = self.gelatto.get_usr_msg()
        time.sleep(2)
        return history_time, usr_msg
    
    # 용어 사전 > 제한 주제 > 새 주제 > 제한 주제 등록
    def register_topic(self):
        info("제한 주제 등록")
        self.gelatto.switch_tab()
        time.sleep(3)
        topic = self.config.get_topic
        # 용어 사전 진입
        self.gelatto.enter_dict()
        self.gelatto.click_constrict_topic()
        time.sleep(2)
        self.gelatto.open_add_topic_modal()
        self.gelatto.add_topic(topic)
        print('제한 주제 등록 OK')
        time.sleep(2)

    # 용어 사전 > 전문 용어 > 새 단어 > 전문 용어 등록
    def register_word(self):
        info("전문 용어 등록")
        self.gelatto.switch_tab()
        time.sleep(3)
        word = self.config.get_input_word
        description = self.config.get_input_description
        # 전문 용어 진입
        self.gelatto.enter_dict()
        self.gelatto.click_professional_word()
        time.sleep(2)
        self.gelatto.open_new_word_modal()
        self.gelatto.add_word_dscr(word, description)
        print('전문 용어 등록 OK')
        time.sleep(2)

    # 대시보드 > 당월 사용 크레딧
    def get_credit_cnt(self):
        info("당월 사용 크레딧 확인")
        info(f"[Credit] handle={self.driver.current_window_handle}")
        info(f"[Credit] url={self.driver.current_url}")
        info(f"[Credit] title={self.driver.title}")
        info(f"[Credit] handles={self.driver.window_handles}")

        self.gelatto.switch_tab()
        self.driver.refresh()
        time.sleep(3)
        self.gelatto.enter_dashboard()
        time.sleep(3)
        return self.gelatto.credit_usage()

        