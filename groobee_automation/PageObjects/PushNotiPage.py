import time
from selenium.common import TimeoutException

from PageObjects.GroobeeActions import GroobeeActions
from utilities.BaseClass import BaseClass
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

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

    # 리스트 > 캠페인명
    campaign_row_by_name = (By.XPATH, "//div[@role='row']//div[contains(text(),\"[HS] 푸시_스케쥴_세그먼트_단일발송 테스트 캠페인\")]")

    #리스트 >Tab
    schedule_send_tab = (By.XPATH, "//button[@role='tab' and normalize-space(.)='스케줄 발송']")
    eventTrigger_send_tab = (By.XPATH, "//button[@role='tab' and normalize-space(.)='이벤트 트리거 발송']")
    apiTrigger_send_tab = (By.XPATH, "//button[@role='tab' and normalize-space(.)='API 트리거 발송']")
    completed_tab =(By.XPATH, "//button[@role='tab' and normalize-space(.)='완료 캠페인']")

    #캠페인명 검색
    campaign_search =(By.XPATH, "//input[contains(@placeholder, '캠페인명 검색')]")

    # 타겟팅 유형
    type_segment = (By.XPATH, "//input[@value='세그먼트']")
    type_recipient_consent = (By.XPATH, "//label[.//input[@value='수신 동의자 전체']]")
    type_member_upload =(By.XPATH, "//label[.//input[@value='회원 정보 업로드']]")

    # 세그먼트 불러오기 RNB(설정할 값 실제 작성)
    qa_hs_seg = (By.XPATH, "//h6[contains(text(),'[QA][HS] OFFSITE_회원ID_세그먼트용')]")

    # 세그먼트 설정* > 불러온 세그먼트
    is_qa_hs_seg =(By.XPATH, "//h6[contains(text(),'[QA][HS] OFFSITE_회원ID_세그먼트용')]")
    # 메시지 설정 - 서브 타이틀
    push_subtitle_msg = (By.XPATH, "//h6[contains(text(),'메시지 기본 설정')]")

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
    default_img_setting = (By.XPATH, "//label[.//span[normalize-space()='설정 값 사용']]")
    # 본문 이미지는 파일 업로드 RNB 공용 사용
    # 본문 > 이미지 파일 업로드 확인
    uploaded_body_image_file_name= (By.XPATH, "//h6[text()='pushNoti_test_img.jpg']")
    # 본문 > 회원 정보 업로드 확인
    uploaded_body_csv_file_name=(By.XPATH, f"//*[contains(text(),'push_sample (37).csv')]")
    #수신 거부 표기
    unsubscribe_notice = (By.XPATH, "//div//input[@value='<푸시 수신거부 표기 문구>']")

    #클릭 동작
    launch_app = (By.XPATH, "//label[normalize-space()='앱 실행']")
    deepLink = (By.XPATH, "//input[@value='딥 링크']")
    launch_webBrowser = (By.XPATH, "//label[normalize-space()='웹 브라우저 실행']")

    #클릭 동작 텍스트 박스 > 웹 브라우저 실행
    launch_webBrowser_textArea = (By.XPATH, "//textarea[@placeholder='http:// 또는 https://를 포함한 URL' and not(@aria-hidden)]")
    #클릭 동작 텍스트 박스 > 딥 링크
    deepLink_textArea_AOS =(By.XPATH, "//label[normalize-space(.)='Android*']"
    "/following::textarea[not(@aria-hidden)][1]")
    deepLink_textArea_iOS = (By.XPATH, "//label[normalize-space(.)='iOS*']"
    "/following::textarea[not(@aria-hidden)][1]")

    #고급 옵션
    advanced_options = (By.XPATH, "//button[contains(text(),'옵션 추가')]")
    advanced_options_key = (By.XPATH, "//input[@placeholder='Key']")
    advanced_options_value = (By.XPATH, "//input[@placeholder='Value']")
    advanced_options_cancel =  (By.XPATH, "/html/body/div/div[3]/div/div/div/div[3]/div/div[3]/div/div[2]/div[1]/div/div[7]/div[2]/div/div/div/button/svg")


    #미리보기
    preview_title = (By.XPATH, "//p[contains(@class,'MuiTypography-root') and contains(text(),'푸시 알림 캠페인')]")
    preview_content = (By.XPATH, "//p[contains(@class,'MuiTypography-root') and contains(text(),'내용: 스케쥴 발송 테스트')]")

    # 3단계
    push_subtitle_option = (By.XPATH, "//h6[contains(text(),'스케줄')]")

    # 3단계 옵션 설정
    send_type_repeat = (By.XPATH, "//label[.//span[normalize-space()='반복 발송']]//input[@type='radio']")
    send_type_single = (By.XPATH, "//label[normalize-space()='단일 발송']//input")

    # 발송 기간 > 수동 종료 전까지
    send_period_until_manual = (By.XPATH, "//input[@type='radio' and @value='수동 종료 전까지']")
    # 기간 지정 > 날짜 지정
    send_period_fixed = (By.XPATH, "//input[@type='radio' and @value='기간 지정']")

    # 기간 지정 > 날짜 지정
    # 반복 설정* > 설정하기 btn
    repeat_setBtn = (By.XPATH, "//button[contains(text(),'설정하기')]")

    # 반복 설정 다이얼로그 > [확인][취소] btn
    repeat_dialog_confirm_btn = (By.XPATH, "//button[contains(text(),'확인')]")
    repeat_dialog_cancel_btn = (By.XPATH, "//button[contains(text(),'취소')]")

    # 다이얼로그
    dialog_confirm_btn = (By.XPATH, "//button[contains(text(),'확인')]")
    dialog_cancel_btn = (By.XPATH, "//button[contains(text(),'취소')]")

    # -------------------------동작 선언 영역-------------------------
    # 캠페인 서치바
    def click_campaign_search(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.campaign_search, timeout).click()

    # 만들기 버튼
    def click_create_btn_push_schedule(self, timeout=10):
        BaseClass.wait_clickable(self.driver,self.createBtn_pushNoti_schedule,timeout).click()
    def click_create_btn_push_eventTri(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.createBtn_pushNoti_eventTrigger,timeout).click()
    def click_create_btn_push_apiTri(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.createBtn_pushNoti_apiTrigger,timeout).click()

    # 타겟팅 유형
    def click_type_segment(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.type_segment, timeout).click()
    def click_type_recipient_consent(self, timeout=10):
        el = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.type_recipient_consent)
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(self.type_recipient_consent)
        )
        el.click()
    def click_type_member_upload(self, timeout=10):
        el = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.type_member_upload)
        )
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(self.type_member_upload)
        )
        el.click()

    # 세그먼트 불러오기 RNB(설정할 값 실제 작성)
    def click_qa_hs_seg(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.qa_hs_seg,timeout).click()
    # 세그먼트 설정* > 불러온 세그먼트 가져오기
    def get_is_qa_push_seg(self, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.is_qa_hs_seg, timeout)
        return el.text.strip()

    # 메시지 설정 - 서브 타이틀
    def wait_push_subtitle_msg_visible(self, timeout=10):
        return BaseClass.wait_visible(self.driver, self.push_subtitle_msg, timeout)

    # 메시지 설정- 알림 목적
    def click_ad_type(self):
        el = BaseClass.wait_visible(self.driver, self.ad_type)
        el.click()
        return self
    def click_info_type(self):
        el = BaseClass.wait_visible(self.driver, self.info_type)
        el.click()
        return self
    # 메시지 설정 > 알림 목적 일치 확인
    def get_is_info_type(self, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.info_type, timeout)
        print("tag:", el.tag_name)
        print("text:", el.text)
        print("value:", el.get_attribute("value"))
        print("checked:", el.get_attribute("checked"))
        return el.text.strip()

    def get_is_ad_type(self, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.ad_type, timeout)
        return el.text.strip()


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

    def click_default_img_setting(self, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.default_img_setting, timeout)
        self.driver.execute_script("arguments[0].click();", el)
        return self

    def send_unsubscribe_notice(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.unsubscribe_notice, timeout)
        el.click()
        time.sleep(1)
        el.send_keys(Keys.COMMAND + "a")  # Mac
        el.send_keys(Keys.DELETE)
        time.sleep(1)
        el.send_keys(text)


    # 미리보기
    def is_preview_text_contains(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.preview_area, timeout)
        return text in el.text

    def is_preview_img_visible(self, timeout=10):
        return BaseClass.wait_visible(self.driver, self.preview_img, timeout)

    def get_preview_url(self, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.preview_url, timeout)
        return el.get_attribute("href").strip()

    def is_preview_url_match(self, timeout=10):
        created = self.get_created_short_url(timeout)
        preview = self.get_preview_url(timeout)
        return created == preview

    #리스트 내용 입력
    def send_campaign_search(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.campaign_search, timeout)
        el.clear()
        el.send_keys(text)
        el.send_keys(Keys.ENTER)


    #클릭 동작
    def click_launch_app(self, timeout=10):
        el = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(self.launch_app)
        )
        el.click()
    def click_deepLink(self, timeout=10):
        BaseClass.select_radio(self.driver, self.deepLink,timeout).click()

    def click_launch_webBrowser(self, timeout=10):
        el = WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(self.launch_webBrowser)
        )
        el.click()
    #클릭 동작 > 딥 링크 텍스트 박스
    def send_deepLink_testArea_AOS(self,text, timeout=10):
        el = (BaseClass.wait_visible(self.driver,self.deepLink_textArea_AOS,timeout))
        el.click()
        el.clear()
        el.send_keys(text)
    def send_deepLink_testArea_iOS(self,text, timeout=10):
        el = (BaseClass.wait_visible(self.driver,self.deepLink_textArea_iOS,timeout))
        el.click()
        el.clear()
        el.send_keys(text)

    # 클릭 동작 > 웹 브라우저 텍스트 박스
    def send_launch_webBrowser(self, text, timeout=10):
        el =(BaseClass.wait_visible(self.driver, self.launch_webBrowser_textArea, timeout))
        el.click()
        el.clear()
        el.send_keys(text)

    #고급 옵션
    def click_advanced_options(self, timeout=10):
        BaseClass.wait_visible(self.driver,self.advanced_options,timeout).click()
    def click_advanced_options_key(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.advanced_options_key, timeout)
        el.clear()
        el.send_keys(text)
    def click_advanced_options_value(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.advanced_options_value, timeout)
        el.clear()
        el.send_keys(text)
    def click_advanced_options_cancel(self, timeout=10):
        btn = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.advanced_options_cancel)
        )
        WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable(self.advanced_options_cancel)
        )
        btn.click()

    # 3단계 > 옵션 설정 서브타이틀
    def wait_push_subtitle_option_visible(self, text="스케줄", timeout=10):
        locator = (By.XPATH, f"//h6[normalize-space()='{text}']")
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
    # 3단계 > 단일, 반복 발송
    def click_send_type_single(self, timeout=10):
        BaseClass.select_radio(self.driver, self.send_type_single, timeout).click()

    def click_send_type_repeat(self, timeout=15):
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.send_type_repeat)
        )
        el = self.driver.find_element(*self.send_type_repeat)
        self.driver.execute_script("arguments[0].click();", el)

    #다이얼로그 > [확인][취소] btn
    def click_dialog_confirm_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.dialog_confirm_btn, timeout).click()
    def click_dialog_cancel_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.dialog_cancel_btn, timeout).click()


    # 스크롤 ver.1
    def scroll_to(self, element):
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", element
        )
        return self

    # 스크롤 ver.2
    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # 캠페인 리스트 > 캠페인 일치 찾기
    def search_campaign_row_by_name(self, campaign_name):
        return (
            By.XPATH,
            f"//div[@role='row']//div[contains(text(),'{campaign_name}')]"
        )

    #======== 검증 영역 =================#
    def assert_searched_campaign_matches(self, expected_campaign_name):
        """
        검색된 캠페인명과
        실제 리스트에 노출된 캠페인명이 일치하는지 검증
        """

        campaign_elements = self.get_campaign_name_list()

        # 검색 결과 존재 여부 확인
        assert len(campaign_elements) > 0, (
            f"[FAIL] 검색 결과 없음: {expected_campaign_name}"
        )

        # 캠페인명 리스트 추출
        campaign_names = [el.text.strip() for el in campaign_elements]

        # 기대값이 리스트에 포함되어 있는지 확인
        assert any(expected_campaign_name in name for name in campaign_names), (
            f"[FAIL] 검색 결과 불일치\n"
            f" - 검색어: {expected_campaign_name}\n"
            f" - 노출 캠페인 리스트: {campaign_names}"
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

    # 진행 중 캠페인 존재 여부 체그
    def is_campaign_playing(self, cam_name):
        """
        특정 캠페인이 '재생중(진행중)' 상태인지 확인
        """
        try:
            play_icon = self.driver.find_element(
                By.XPATH,
                f"//tr[td[contains(text(),'{cam_name}')]]//button[contains(@class,'pause')]"
            )
            return play_icon.is_displayed()
        except:
            return False


    # ===== 미리보기 일치 =========================== #

    # 미리보기 > 제목
    def preview_title_by_text(self, title_text):
        return (
            By.XPATH,
            f"//p[contains(@class,'MuiTypography-root') and contains(text(),'{title_text}')]"
        )

    #  미리보기 영역 > wrapper 먼저 잡기
    def get_push_preview_area(self):
        return self.driver.find_element(
            By.XPATH,
            "//div[contains(@class,'MuiPaper-root') and .//p[contains(text(),'내용')]]"
        )
    # 미리보기 > 내용 입력 검증
    def assert_push_preview_message(self, expected_message):

        preview_area = self.get_push_preview_area()
        preview_text = preview_area.text

        assert expected_message in preview_text, (
            f"[FAIL] 미리보기 내용 불일치\n"
            f" - 기대값: {expected_message}\n"
            f" - 실제값: {preview_text}"
        )
    # 미리보기 > 수신 거부 내용 입력 검증
    def assert_push_preview_unsubscribe(self, expected_unsubscribe_text):

        preview_area = self.get_push_preview_area()
        preview_text = preview_area.text

        assert expected_unsubscribe_text in preview_text, (
            f"[FAIL] 수신거부 문구 불일치\n"
            f" - 기대값: {expected_unsubscribe_text}\n"
            f" - 실제값: {preview_text}"
        )
    # 기본 이미지 > 설정 체크 검증
    def assert_default_preview_image_visible(self):
        img = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//img")
            )
        )
        assert img.is_displayed(), "[FAIL] 미리보기 이미지가 표시되지 않음"
    # 기본 이미지 > 미리보기 url 및 none 아님 확인
    def assert_default_preview_image(self):
        img_element = self.driver.find_element(
            By.XPATH,
            "//img[contains(@class,'MuiAvatar-img')]"
        )
        actual_src = img_element.get_attribute("src")
        assert actual_src is not None and actual_src != "", \
            "[FAIL] 이미지 src가 비어 있음"
        assert "app_default_img" in actual_src, \
            f"[FAIL] 기본 이미지 경로 아님: {actual_src}"
        assert actual_src.endswith(".png"), \
            f"[FAIL] PNG 이미지 아님: {actual_src}"

    # 본문 > 파일 업로드 확인 * image
    def assert_uploaded_body_image_file_name(self, expected_file_name):
        element = self.driver.find_element(
            By.XPATH,
            f"//h6[contains(text(),'{expected_file_name}')]"
        )
        assert element.is_displayed(), \
            f"[FAIL] 업로드 파일명 불일치: {expected_file_name}"

    # 본문 > 파일 csv 확인
    def assert_uploaded_body_csv_file_name(self, expected_file_name_member, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//span[contains(@class,'MuiChip-label') and contains(text(),'{expected_file_name_member}')]")
            )
        )

        element = self.driver.find_element(
            By.XPATH,
            f"//span[contains(@class,'MuiChip-label') and contains(text(),'{expected_file_name_member}')]"
        )

        assert element.is_displayed(), f"[CSV 업로드 실패] {expected_file_name_member} 표시 안됨"

    # 딥 링크 > AOS 입력값 검증
    def assert_deepLink_textArea_AOS(self, expected_value):
        actual_value = self.driver.find_element(
            *self.deepLink_textArea_AOS
        ).get_attribute("value")

        assert expected_value == actual_value, (
            f"[FAIL] AOS 딥링크 불일치\n"
            f" - 기대값: {expected_value}\n"
            f" - 실제값: {actual_value}"
        )
    # 딥 링크 > iOS 입력값 검증
    def assert_deepLink_textArea_iOS(self, expected_value):
        actual_value = self.driver.find_element(
            *self.deepLink_textArea_iOS
        ).get_attribute("value")

        assert expected_value == actual_value, (
            f"[FAIL] iOS 딥링크 불일치\n"
            f" - 기대값: {expected_value}\n"
            f" - 실제값: {actual_value}"
        )
    # 웹 브라우저 > 입력값 검증
    def assert_launch_webBrowser(self, Offsite_webBrowser, timeout=10):
        el = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.launch_webBrowser_textArea)
        )

        actual_value = el.get_attribute("value")

        assert actual_value == Offsite_webBrowser, \
            f"[FAIL] 웹브라우저 URL 불일치\n기대값: {Offsite_webBrowser}\n실제값: {actual_value}"

    # 고급 옵션 > key 입력값 검증
    def assert_advanced_options_key(self, expected_value):
        actual_value = self.driver.find_element(
            *self.advanced_options_key
        ).get_attribute("value")

        assert expected_value == actual_value, (
            f"[FAIL] 고급 옵션 Key 불일치\n"
            f" - 기대값: {expected_value}\n"
            f" - 실제값: {actual_value}"
        )
    # 딥 링크 > value 입력값 검증
    def assert_advanced_options_value(self, expected_value):
        actual_value = self.driver.find_element(
            *self.advanced_options_value
        ).get_attribute("value")

        assert expected_value == actual_value, (
            f"[FAIL] 고급 옵션 Vaule 불일치\n"
            f" - 기대값: {expected_value}\n"
            f" - 실제값: {actual_value}"
        )

    # 3단계 > 옵션 노출 확인
    def assert_send_type_options_exist(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.send_type_single)
        )

        single_option = self.driver.find_elements(*self.send_type_single)
        repeat_option = self.driver.find_elements(*self.send_type_repeat)

        assert len(single_option) > 0, "[FAIL] '단일 발송' 옵션이 존재하지 않습니다."
        assert len(repeat_option) > 0, "[FAIL] '반복 발송' 옵션이 존재하지 않습니다."

    # 재생 중인 캠페인이 없어 다이얼로그 없음 -> pass
    def stop_campaign_if_running(self, cam_name):
        try:
            self.click_play_icon_by_name(cam_name)

            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(self.dialog_confirm_btn)
            )

            self.click_dialog_confirm_btn()

        except TimeoutException:
            pass

    # 진행 중 캠페인 > 중지 중 변경
    def stop_all_running_campaigns(self):

        while True:
            pause_buttons = self.driver.find_elements(
                By.XPATH,
                "//button[contains(@class,'pause')]"
            )

            if not pause_buttons:
                break

            pause_buttons[0].click()

            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(self.dialog_confirm_btn)
            )

            self.click_dialog_confirm_btn()

            WebDriverWait(self.driver, 5).until(
                EC.staleness_of(pause_buttons[0])
            )