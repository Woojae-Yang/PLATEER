
import os
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from setup.base_action import BaseAction
import setup.selenium_utils as util
from setup.logger import info

class GelattoProduct(BaseAction):

    def __init__(self, driver, wait, tab):
        self.driver = driver
        self.wait = wait
        self.tab = tab
    
    # -------------------------element 선언 영역-------------------------
    
    ## LNB
    lnb_dashboard = (By.XPATH, "//*[contains(normalize-space(.), '대시보드')]")
    lnb_knwoledge = (By.XPATH, "//*[contains(normalize-space(.), '지식 센터')]")
    lnb_make_gelatto = (By.XPATH, "//*[contains(normalize-space(.), '젤라또 만들기')]")
    lnb_dict = (By.XPATH, "//*[contains(normalize-space(.), '용어 사전')]")
    lnb_report = (By.XPATH, "//*[contains(normalize-space(.), '분석 리포트')]")

    ## DashBoard -------------------------
    ### [최근 활동 내역] RNB 진입 버튼
    log_history_btn = (By.XPATH, "//button[contains(text(), '최근 활동 내역')]")
    ### [최근 활동 내역] > 1번째 내용
    recent_log = (By.XPATH, "/html/body/div[2]/div[3]/div/div/div[2]/div[1]/div[1]")
    ### 당월 사용 크레딧
    used_credit = (By.XPATH, "/html/body/div/div[3]/div/div/div/div[2]/div/div[3]/div[2]/h5")
                
    ## 젤라또 만들기 -------------------------
    ### 기본 설정 탭
    setting_tab = (By.XPATH, "//button[contains(text(), '기본 설정')]")
    #### 대표 문구
    represnt_txt_box = (By.XPATH, "/html/body/div/div[3]/div/div/div/div[3]/div[2]/div/div/div/div/div[2]/div[1]/div[6]/div[2]/div/div/input")
    #### 첫인사
    hello_box = (By.XPATH, "/html/body/div/div[3]/div/div/div/div[3]/div[2]/div/div/div/div/div[2]/div[1]/div[7]/div[2]/div/div/textarea[1]")
    #### 플레이스홀더
    placeholder = (By.XPATH, "/html/body/div/div[3]/div/div/div/div[3]/div[2]/div/div/div/div/div[2]/div[1]/div[8]/div[2]/div/div/input")
    #### 저장 btn
    save_btn = (By.XPATH, "//button[contains(text(), '저장')]")


    ## 용어 사전 -------------------------
    ### 제한 주제 탭
    constrict_topic = (By.XPATH, "//button[contains(text(), '제한 주제')]")
    #### 제한 주제 > 새 주제 btn
    new_topic_btn = (By.XPATH, "/html/body/div/div[3]/div/div/div/div[2]/div[2]/div[2]/button")
    ##### [제한 주제 등록] 모달
    add_topic_modal = (By.XPATH, "/html/body/div[2]/div[3]/div")
    ##### [제한 주제 등록] > 제한 주제
    topic_box = (By.XPATH, '/html/body/div[2]/div[3]/div/div[1]/div/div[2]/div[2]/div/div/input')
    ##### [제한 주제 등록] > 등록 btn
    add_btn = (By.XPATH, "/html/body/div[2]/div[3]/div/div[2]/button[2]")

    ### 전문 용어 탭 
    professional_word = (By.XPATH, "//button[contains(text(), '전문 용어')]")
    #### 전문 용어 > 새 단어 btn
    new_word_btn = (By.XPATH, "//button[contains(text(), '새 단어')]")
    #### [전문 용어 등록] 모달
    add_word_modal = (By.XPATH, "/html/body/div[2]/div[3]/div")
    #### [전문 용어 등록] > 단어
    word_box = (By.XPATH, '/html/body/div[2]/div[3]/div/div[1]/div/div[1]/div[2]/div/div/input')
    #### [전문 용어 등록] > 정의
    description_box = (By.XPATH, '/html/body/div[2]/div[3]/div/div[1]/div/div[2]/div[2]/div/div/input')
    #### [전문 용어 등록] > 등록 btn
    add_btn_word = (By.XPATH, "/html/body/div[2]/div[3]/div/div[2]/button[2]")

    ## 분석 리포트 -------------------------
    ### 조회 기간
    period_dropdown = (By.XPATH, "/html/body/div/div[3]/div/div/div/div[2]/div/div[1]/div[2]/div[1]/div")
    ### 조회 기간 선택 : "6시간"
    dropdown_6h = (By.XPATH, "li[contains(text(), '6시간')]")
    ### 봇 내역 탭
    bot_history_tab = (By.XPATH, "//button[contains(text(), '봇 내역')]")
    ### 봇 분석 탭
    bot_analy_tab = (By.XPATH, "//button[contains(text(), '봇 분석')]")

    #### 봇 분석 탭 > 챗봇 응답 대화 건수
    conversation_response = (By.XPATH, "/html/body/div/div[3]/div/div/div/div[2]/div/div[3]/div[1]/h6")
    #### 봇 분석 탭 > 챗봇 응답 메세지 수
    msg_response = (By.XPATH, "/html/body/div/div[3]/div/div/div/div[2]/div/div[3]/div[2]/h6")
    #### 봇 분석 탭 > 평균 응답 메세지 수
    avg_response = (By.XPATH, "/html/body/div/div[3]/div/div/div/div[2]/div/div[3]/div[3]/h6")
    
    #### 봇 내역 탭 > 데이터 테이블
    ##### 내역 일시
    history_time_elem = (By.XPATH, "/html/body/div/div[3]/div/div/div/div[2]/div/div[3]/div[3]/div[1]/div[2]/div/div/div[1]/div[1]/p")
    usr_msg_elem = (By.XPATH, "/html/body/div/div[3]/div/div/div/div[2]/div/div[3]/div[3]/div[1]/div[2]/div/div/div[1]/div[3]/p")

    # -------------------------동작 선언 영역-------------------------

    def switch_tab(self):
        self.driver.switch_to.window(self.tab)
        time.sleep(2)

    ######################## 대시보드 활동 -------------------------
    def enter_dashboard(self):
        info("대시보드 LNB")
        self.wait_and_click(EC.element_to_be_clickable, self.lnb_dashboard, "LNB 대시보드 진입")
        time.sleep(3)

    def enter_log_rnb(self):
        info("최근 활동 RNB")
        self.wait_and_click(EC.element_to_be_clickable, self.log_history_btn, "최근 활동 RNB 호출")
        time.sleep(3)

    def get_recent_log(self):
        time.sleep(2)
        info("최근 활동 내역 조회")
        return self.find(self.recent_log, "최근 활동 내역 조회").text

    def get_credit_cnt(self):
        info("당월 사용 크레딧")
        self.wait_and_click(EC.presence_of_element_located, self.used_credit, "당월 사용 크레딧")
        print(self.find(self.used_credit, "당월 사용 크레딧").text)
        return self.find(self.used_credit, "당월 사용 크레딧").text

    ######################## 젤라또 만들기 활동 -------------------------
    #### 젤라도 만들기 진입
    def enter_make_gelatto(self):
        time.sleep(2)
        info("젤라또 만들기 진입")
        self.wait_and_click(EC.element_to_be_clickable, self.lnb_make_gelatto, "LNB 젤라또 만들기 클릭")
        time.sleep(3)

    #### 기본 설정 탭
    def click_setting_tab(self):
        time.sleep(2)
        info("기본 설정 탭")
        self.wait_and_click(EC.presence_of_element_located, self.setting_tab, "기본 설정 탭 클릭")
        time.sleep(2.5)
    
    #### 기본값 설정 정보 입력
    def input_values(self):
        time.sleep(2)
        info("[Input_values] 기본값 설정 정보 입력")
        # 대표 문구
        self.input(self.represnt_txt_box, "Automation Test", "대표 문구")
        # 첫인사
        self.input(self.hello_box, "Hello Gelatto", "첫 인사")
        # 플레이스홀더
        self.input(self.placeholder, "Automation Placeholder", "플레이스홀더")
        time.sleep(2.5)
        info("[Input_values] 기본값 설정 정보 입력 완료")

    def click_save(self):
        time.sleep(2)
        info("저장하기")
        self.wait_and_click(EC.element_to_be_clickable, self.save_btn, "저장 버튼")
        time.sleep(3)
        ## 모달에서 확인 클릭
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div/div[2]/button[2]").click()
        info("저장 완료")
    
    ######################## 용어 사전 활동 -------------------------
    #### 용어 사전 진입
    def enter_dict(self):
        info("용어 사진 진입")
        self.wait_and_click(EC.element_to_be_clickable, self.lnb_dict, "LNB 용어 사전")
        time.sleep(2.5)
    
    ##### 제한 주제 탭 클릭
    def click_constrict_topic(self):
        info("제한 주제")
        self.wait_and_click(EC.element_to_be_clickable, self.constrict_topic, "제한 주제")
        time.sleep(2.5)
    
    ##### 새 주제 버튼 클릭
    def open_add_topic_modal(self):
        info("새 주제")
        self.wait_and_click(EC.element_to_be_clickable, self.new_topic_btn, "새 주제")
        time.sleep(2.5)
    
    ##### 제한 주제 등록
    def add_topic(self, topic):
        info("제한 주제")
        self.find(self.topic_box, "제한 주제 등록").send_keys(f'[AUTO] topic')
        time.sleep(3)
        self.wait_and_click(EC.element_to_be_clickable, self.add_btn, "등록 버튼 클릭")
        time.sleep(2)
        
    ##### 전문 용어 탭 클릭
    def click_professional_word(self):
        info("전문 용어")
        self.wait_and_click(EC.element_to_be_clickable, self.professional_word, "전문 용어 탭")
        time.sleep(2)
    
    ##### 새 단어 버튼 클릭
    def open_new_word_modal(self):
        info("새 단어")
        self.wait_and_click(EC.element_to_be_clickable, self.new_word_btn, "새 단어")
        time.sleep(2)

    ##### 새 단어 등록
    def add_word_dscr(self, word, description):
        time.sleep(2)
        info("새 단어 등록")
        self.find(self.word_box, "단어 텍스트박스").send_keys(f'[AUTO] word')
        self.find(self.description_box, "정의 텍스트박스").send_keys(f'[AUTO] description')
        time.sleep(2)
        self.wait_and_click(EC.presence_of_element_located, self.add_btn_word, "등록 버튼")
        info("새 단어 등록 완료")
        time.sleep(1.5)
    
    ######################## 분석 리포트 활동 -------------------------
    #### 분석 리포트 진입
    def enter_report(self):
        time.sleep(2)
        info("분석리포트 진입")
        self.wait_and_click(EC.element_to_be_clickable, self.lnb_report, "LNB 분석리포트")
        time.sleep(2)

    def select_period(self):
        time.sleep(2)
        info("조회 기간")
        self.wait_and_click(EC.element_to_be_clickable, self.period_dropdown, "기간 드롭다운 박스")
        self.wait_and_click(EC.element_to_be_clickable, self.dropdown_6h, "6시간")
        print("조회 기간 : 6시간")
                                                              
    #### 봇 분석 탭 진입
    def enter_bot_analy(self):
        time.sleep(2)
        info("봇 분석 탭 진입")
        self.wait_and_click(EC.element_to_be_clickable, self.bot_analy_tab, "봇 분석 탭")
        time.sleep(2)
    
    ##### 챗봇 응답 대화 수 출력
    def get_conversation_cnt(self):
        time.sleep(2)
        info("응답 대화 수")
        return self.find(self.conversation_response, "응답 대화 수")
    
    ##### 챗봇 응답 메세지 수 출력
    def get_msg_cnt(self):
        time.sleep(2)
        info("응답 메세지 수")
        return self.find(self.msg_response, "응답 메세지 수").text
    
    ##### 평균 응답 메세지 수 출력
    def get_avg_cnt(self):
        time.sleep(2)
        info("평균 응답 메세지 수")
        return self.find(self.avg_response, "평균 응답 메세지 수 ").text

    #### 봇 내역 탭 진입
    def enter_bot_history(self):
        info("봇 내역 탭 진입")
        self.wait_and_click(EC.element_to_be_clickable, self.bot_history_tab, "봇 내역 탭")
        time.sleep(2)

    ##### 데이터 테이블 > 내역 일시
    def get_history_date(self):
        time.sleep(2)
        info("데이터 테이블 > 내역 일시")
        # 내역 일시
        return self.find(self.history_time_elem, "내역 일시").text
        
    ##### 데이터 테이블 > 사용자 메세지
    def get_usr_msg(self):
        time.sleep(2)
        info("데이터 테이블 > 사용자 메세지")
        return self.find(self.usr_msg_elem, "사용자 메세지").text
        
    
