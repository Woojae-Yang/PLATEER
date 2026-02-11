import time

from selenium.webdriver.common.by import By
from PageObjects.GroobeeActions import GroobeeActions
from utilities.BaseClass import BaseClass
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

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

    #리스트 >Tab
    schedule_send_tab = (By.XPATH, "//button[@role='tab' and normalize-space(.)='스케줄 발송']")
    eventTrigger_send_tab = (By.XPATH, "//button[@role='tab' and normalize-space(.)='이벤트 트리거 발송']")
    apiTrigger_send_tab = (By.XPATH, "//button[@role='tab' and normalize-space(.)='API 트리거 발송']")
    completed_tab =(By.XPATH, "//button[@role='tab' and normalize-space(.)='완료 캠페인']")

    #캠페인명 검색
    campaign_search =(By.XPATH, "//input[contains(@placeholder='캠페인명 검색')]")
    #캠페인 리스트 > 해당 캠페인 명 찾기


    # 타겟팅 유형
    #type_segment =(By.XPATH, "//button[.//text()[contains(.,'세그먼트')]]")
    type_segment = (By.XPATH, "//input[@value='세그먼트']")
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

    # 내용 입력 <문제> 한글 공백 포함 최대 31자
    message_step = (By.XPATH, "//h6[contains(text(),'메시지 작성')]")
    message_title = (By.XPATH, "/html/body/div/div[3]/div/div/div/div[3]/div/div[3]/div/div[2]/div[1]/div/div[1]/div[2]/div/div/input")
    message_contents = (By.XPATH, "/html/body/div/div[3]/div/div/div/div[3]/div/div[3]/div/div[2]/div[1]/div/div[2]/div[2]/div/div/textarea[1]")


    #기본 이미지 - 설정 값 사용
    #default_img_setting =  (By.XPATH, "//span[normalize-space(.)='설정 값 사용']"
    #"/preceding-sibling::span//input[@type='checkbox']")
    default_img_setting = (By.XPATH, "//label[.//span[normalize-space()='설정 값 사용']]")
    #본문 이미지는 파일 업로드 RNB 공용 사용

    #수신 거부 표기
    unsubscribe_notice = (By.XPATH, "//div//input[@value='<푸시 수신거부 표기 문구>']")

    #클릭 동작
    launch_app = (By.XPATH, "//input[@value='앱 실행']")
    deepLink = (By.XPATH, "//input[@value='딥 링크']")
    launch_webBrowser_ = (By.XPATH, "//input[@value='웹 브라우저 실행']")

    #클릭 동작 텍스트 박스
    deepLink_textArea_AOS =(By.XPATH,"//label[normalize-space(.)='Android*']"
    "/following::textarea[not(@aria-hidden)][1]")
    deepLink_textArea_iOS = (By.XPATH,
    "//label[normalize-space(.)='iOS*']"
    "/following::textarea[not(@aria-hidden)][1]")

    #고급 옵션
    advanced_options = (By.XPATH, "//button[contains(text(),'옵션 추가')]")
    advanced_options_key = (By.XPATH, "//input[@placeholder='Key']")
    advanced_options_value = (By.XPATH, "//input[@placeholder='Value']")

    #미리 보기: mo_버튼존재

    #3단계 옵션 설정
    send_type_single = (By.XPATH, "//input[@value='단일 발송']")
    send_type_repeat = (By.XPATH, "//input[@value='반복 발송']")

    # 다이얼로그
    dialog_confirm_button = (By.XPATH, "//button[contains(text(),'확인')]")
    dialog_cancel_button = (By.XPATH, "//button[contains(text(),'취소')]")

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
        BaseClass.select_radio(self.driver, self.type_segment,timeout)
    def click_type_recipient_consent(self, timeout=10):
        BaseClass.select_radio(self.driver, self.type_recipient_consent,timeout)
    def click_type_member_upload(self, timeout=10):
        BaseClass.select_radio(self.driver, self.type_member_upload,timeout)

    # 세그먼트 불러오기 RNB(설정할 값 실제 작성)
    def click_qa_hs_seg(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.qa_hs_seg,timeout).click()

    # 메시지 설정- 알림 목적
    def click_ad_type(self):
        el = BaseClass.wait_visible(self.driver, self.ad_type)
        el.click()
        return self
    def click_info_type(self):
        el = BaseClass.wait_visible(self.driver, self.info_type)
        el.click()
        return self

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

    #내용 클릭
    def click_message_step(self, timeout=10):
        BaseClass.wait_visible(self.driver, self.message_step,timeout).click()
        return self

    def click_message_title(self, timeout=10):
        BaseClass.wait_visible(self.driver, self.message_title, timeout).click()
        return self

    def click_message_content(self, timeout=10):
        BaseClass.wait_visible(self.driver, self.message_contents,timeout).click()

    def click_unsubscribe_notice(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.unsubscribe_notice,timeout).click()

    #내용 입력
    def send_message_title(self, text, timeout=10):
        el =BaseClass.wait_visible(self.driver, self.message_title, timeout)
        el.clear()
        el.send_keys(text)
        return self
    def send_message_contests(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.message_contents, timeout)
        el.clear()
        el.send_keys(text)
    #def click_default_img_setting(self, text, timeout=10):
    #    BaseClass.wait_clickable(self.driver,self.default_img_setting,timeout).click()

    def click_default_img_setting(self, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.default_img_setting, timeout)
        self.driver.execute_script("arguments[0].click();", el)
        return self

    def send_unsubscribe_notice(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.unsubscribe_notice, timeout)
        el.click()
        el.send_keys(Keys.COMMAND + "a")  # Mac
        el.send_keys(Keys.DELETE)
        el.send_keys(text)

    #리스트 내용 입력
    def send_campaign_search(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.campaign_search, timeout)
        el.clear()
        el.send_keys(text)


    #클릭 동작
    def click_launch_app(self, text, timeout=10):
        BaseClass.wait_clickable(self.driver,self.img_setting,timeout).click()

    def click_deepLink(self, timeout=10):
        el = BaseClass.wait_clickable(self.driver, self.deepLink, timeout)
        el.click()
        return self

    def click_launch_webBrowser(self, text, timeout=10):
        BaseClass.wait_clickable(self.driver,self.launch_webBrowser, timeout).click()
    #클릭 동작 텍스트 박스
    def send_deepLink_testArea_AOS(self,text, timeout=10):
        el = BaseClass.wait_visible(self.driver,self.deepLink_textArea_AOS,timeout).click()
        el.clear()
        el.send_keys(text)
    def send_deepLink_testArea_iOS(self,text, timeout=10):
        el = BaseClass.wait_visible(self.driver,self.deepLink_textArea_iOS,timeout).click()
        el.clear()
        el.send_keys(text)


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

    #다이얼로그
    def click_dialog_confirm_button(self, text, timeout=10):
        BaseClass.wait_clickable(self.driver, self.dialog_confirm_button, timeout).click()
    def click_dialog_cancel_button(self, text, timeout=10):
        BaseClass.wait_clickable(self.driver, self.dialog_cancel_button, timeout).click()


    # 스크롤
    def scroll_to(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", element
        )
        return self

    #======== 검증 영역 =================#
    def assert_searched_campaign_matches(groobee, Push_sched_expected_campaign_name):
        """
        검색된 캠페인명과
        실제 리스트에 노출된 캠페인명이 일치하는지 검증
        """

        campaign_elements = groobee.get_campaign_name_list()

        assert len(campaign_elements) > 0, (
            f"[FAIL] 검색 결과 없음: {Push_sched_expected_campaign_name}"
        )

        for el in campaign_elements:
            actual_name = el.text.strip()
            assert Push_sched_expected_campaign_name in actual_name, (
                f"[FAIL] 검색 결과 불일치\n"
                f" - 검색어: {Push_sched_expected_campaign_name}\n"
                f" - 노출 캠페인: {actual_name}"
            )

    def assert_page_title_matches(driver, expected_title, timeout=5, pushNoti_title=None):
        assert pushNoti_title is not None, "pushNoti title 전달되지 않았습니다."
        """
        pushNoti_title locator로 찾은 타이틀과
        실제 페이지에 노출된 문자열이 일치하는지 검증
        """

        title_element = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located(pushNoti_title)
        )

        actual_title = title_element.text.strip()

        assert actual_title == expected_title, (
            f"[FAIL] 페이지 타이틀 불일치\n"
            f" - 기대값: {expected_title}\n"
            f" - 실제값: {actual_title}"
        )

    def get_seg_list(self):
        return self.driver.find_elements(*self.qa_hs_seg)

    def click_first_seg(self):
        segs = self.get_seg_list()
        if segs:
            segs[0].click()
        return self
        