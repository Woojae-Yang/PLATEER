import time

from selenium.webdriver.common.by import By
from PageObjects.GroobeeActions import GroobeeActions
from utilities.BaseClass import BaseClass

class PushNotiPage(GroobeeActions):
    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver


    # -------------------------element 선언 영역-------------------------
    # 만들기 버튼
    createBtn_pushNoti_schedule = (By.XPATH, "//li[contains(text(),'스케줄 발송')]")
    createBtn_pushNoti_eventTrigger = (By.XPATH, "//li[contains(text(),'이벤트 트리거 발송')]")
    createBtn_pushNoti_apiTrigger = (By.XPATH, "//li[contains(text(),'API 트리거 발송')]")

    # 타이틀
    schedule_cam_title = (By.XPATH, "//h1[contains(text(),'새로운 푸시 알림 캠페인 만들기')]")
    eventTrigger_cam_title = (By.XPATH, "//h1[contains(text(),'새로운 푸시 알림 캠페인 만들기')]")
    apiTrigger_cam_title = (By.XPATH, "//h1[contains(text(),'새로운 푸시 알림 캠페인 만들기')]")

    # 타겟팅 유형
    type_segment =(By.XPATH, "//input[@value='세그먼트']")
    type_recipient_consent = (By.XPATH, "//input[@value='수신 동의자 전체']")
    type_member_upload =(By.XPATH, "//input[@value='회원 정보 업로드']")


    # 세그먼트 불러오기 RNB(설정할 값 실제 작성)
    qa_hs_seg = (By.XPATH, "//h6[contains(text(),'[QA][HS] OFFSITE_회원ID_세그먼트용')]")

    # 메시지 설정- 알림 목적
    ad_type = (By.XPATH, "//input[@value='광고성']")
    info_type = (By.XPATH, "//input[@value='정보성']")

    #광고 문구 표기
    ad_KR = (By.XPATH, "//li[@data-value='한국어']")
    ad_EN = (By.XPATH, "//li[@data-value='영어']")
    ad_JP = (By.XPATH, "//li[@data-value='일본어']")
    ad_zh_CN = (By.XPATH, "//li[@data-value='중국어 간체']")
    ad_zh_TW = (By.XPATH, "//li[@data-value='중국어 번체(대만)']")
    ad_zh_HK = (By.XPATH, "//li[@data-value='중국어 번체(홍콩)']")

    # 내용 입력
    message_title = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 31자']")
    message_contents = (By.XPATH, "//textarea[@placeholder='한글 공백 포함 최대 210자']")


    #기본 이미지 - 설정 값 사용
    img_setting =  (By.XPATH, "//span[normalize-space(.)='설정 값 사용']"
    "/preceding-sibling::span//input[@type='checkbox']")

    #본문 이미지는 파일 업로드 RNB 공용 사용

    #클릭 동작
    launch_app_ = (By.XPATH, "//input[@value='앱 실행']")
    deepLink = (By.XPATH, "//input[@value='딥 링크']")
    launch_webBrowser_ = (By.XPATH, "//input[@value='웹 브라우저 실행']")

    #고급 옵션
    advanced_options = (By.XPATH, "//button[contains(text(),'옵션 추가')]")
    advanced_options_key = (By.XPATH, "//input[@placeholder='Key']")
    advanced_options_value = (By.XPATH, "//input[@placeholder='Value']")

    #미리 보기: mo_버튼존재

    #3단계 옵션 설정
    send_type_single = (By.XPATH, "//input[@value='단일 발송']")
    send_type_repeat = (By.XPATH, "//input[@value='반복 발송']")

    # -------------------------동작 선언 영역-------------------------
    # 만들기 버튼
    def click_create_btn_push_schedule(self, timeout=10):
        BaseClass.wait_clickable(self.driver,self.createBtn_pushNoti_schedule,timeout).click()
    def click_create_btn_push_eventTri(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.createBtn_pushNoti_eventTrigger,timeout).click()
    def click_create_btn_push_apiTri(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.createBtn_pushNoti_apiTrigger,timeout).click()

    # 타겟팅 유형
    def click_type_segment(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.type_segment,timeout).click()
    def click_type_recipient_consent(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.type_recipient_consent,timeout).click()
    def click_type_member_upload(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.type_member_upload,timeout).click()

    # 세그먼트 불러오기 RNB(설정할 값 실제 작성)
    def click_qa_hs_seg(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.qa_hs_seg,timeout).click()

    # 메시지 설정- 알림 목적
    def click_ad_type(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.ad_type,timeout).click()
    def click_info_type(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.info_type,timeout).click()

    #광고 문구 표기 유형
    def click_ad_KR(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.ad_KR,timeout).click()
    def click_ad_EN(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.ad_EN,timeout).click()
    def click_ad_JP(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.ad_JP,timeout).click()
    def click_ad_zh_CN(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.ad_zh_CN,timeout).click()
    def click_ad_zh_TW(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.ad_zh_TW,timeout).click()
    def click_ad_zh_HK(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.ad_zh_HK,timeout).click()

    #내용 입력
    def send_message_title(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.message_title, timeout)
        el.clear()
        el.send_keys(text)
    def send_message_contests(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.message_contents, timeout)
        el.clear()
        el.send_keys(text)
    def click_img_setting(self, text, timeout=10):
        BaseClass.wait_clickable(self.driver,self.img_setting,timeout).click()

    #클릭 동작
    def click_launch_app(self, text, timeout=10):
        BaseClass.wait_clickable(self.driver,self.img_setting,timeout).click()
    def click_deepLink(self, text, timeout=10):
        BaseClass.wait_clickable(self.driver,self.deepLink,timeout).click()
    def click_launch_webBrowser(self, text, timeout=10):
        BaseClass.wait_clickable(self.driver,self.launch_webBrowser, timeout).click()

    #고급 옵션
    def click_advanced_options(self, text, timeout=10):
        BaseClass.wait_clickable(self.driver,self.advanced_options,timeout).click()
    def click_advanced_options_key(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.advanced_options_key, timeout)
        el.clear()
        el.send_keys(text)
    def click_advanced_options_value(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.advanced_options_value, timeout)
        el.clear()
        el.send_keys(text)

    #단일, 반복 발송
    def click_send_type_single(self, text, timeout=10):
        BaseClass.wait_clickable(self.driver, self.send_type_single, timeout).click()
    def click_send_type_repeat(self, text, timeout=10):
        BaseClass.wait_clickable(self.driver, self.send_type_repeat, timeout).click()
