from selenium.webdriver.common.by import By
from PageObjects.GroobeeActions import GroobeeActions
from utilities.BaseClass import BaseClass

class SmsPage(GroobeeActions):

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    # -------------------------element 선언 영역-------------------------
    # 타이틀
    sms_cam_title = (By.XPATH, "//h1[contains(text(),'새로운 SMS 캠페인 만들기')]")

    # 세그먼트 불러오기 RNB(설정할 값 실제 작성)
    qa_gp_seg = (By.XPATH, "//h6[contains(text(),'[QA][GP][Auto] 세그먼트')]")

    # 메시지 설정 서브타이틀
    sms_subtitle_msg = (By.XPATH, "//h6[contains(text(),'메시지 작성')]")

    # 내용
    contents_input = (By.XPATH, "//div[@id='sms-text-content']")

    # 개인화 변수 추가(설정할 값 실제 작성)
    add_personalBtn = (By.XPATH, "//button[contains(text(),'개인화 변수 추가')]")
    add_personal_cbx = (By.XPATH, "//div[@role='combobox']")
    add_personal_auto = (By.XPATH, "//li[contains(text(),'운영테스트')]")
    add_personal_input = (By.XPATH, "//input[@placeholder='값을 입력해 주세요.']")
    add_personal_cancel = (By.XPATH, "(//button[contains(text(),'취소')])[2]")
    add_personal_confirm = (By.XPATH, "//button[contains(text(),'확인')]")

    # 단축 URL
    add_short_urlBtn = (By.XPATH, "//*[contains(.,'단축 URL')]/following::button[normalize-space()='추가'][1]")
    add_short_url_input = (By.XPATH, "//textarea[@placeholder='http:// 또는 https://를 포함한 URL']")
    add_short_url_cancel = (By.XPATH, "(//button[contains(text(),'취소')])[2]")
    add_short_url_confirm = (By.XPATH, "//button[contains(text(),'확인')]")
    created_short_url = (By.XPATH, "(//div[contains(text(),'grb.ai/s/')])[1]")

    # 미리보기
    preview_area = (By.XPATH, "(//button[normalize-space()='발송 테스트']/ancestor::*[.//div[contains(@class,'MuiPaper-root')]][1]//div[contains(@class,'MuiPaper-root')])[1]")
    preview_img = (By.XPATH, "(//img[contains(@src,'/upload_file/')])[2]")
    preview_url = (By.XPATH, "//a[contains(@href,'grb.ai/s/')]")

    # 옵션 설정 서브타이틀
    sms_subtitle_option = (By.XPATH, "//h6[contains(text(),'스케줄')]")

    # -------------------------동작 선언 영역-------------------------

    # 세그먼트 불러오기 RNB(설정할 값 실제 작성)
    def click_qa_gp_seg(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.qa_gp_seg, timeout).click()

    # 메시지 설정 서브타이틀
    def wait_sms_subtitle_msg_visible(self, timeout=10):
        return BaseClass.wait_visible(self.driver, self.sms_subtitle_msg, timeout)

    # 내용
    def send_contents_input(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.contents_input, timeout)
        el.send_keys(text)

    # 개인화 변수 추가(설정할 값 실제 작성)
    def click_add_personal_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.add_personalBtn, timeout).click()
    def click_add_personal_cbx(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.add_personal_cbx, timeout).click()
    def click_add_personal_auto(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.add_personal_auto, timeout).click()
    def send_add_personal_input(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.add_personal_input, timeout)
        el.clear()
        el.send_keys(text)
    def click_add_personal_cancel(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.add_personal_cancel, timeout).click()
    def click_add_personal_confirm(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.add_personal_confirm, timeout).click()

    # 단축 URL
    def click_add_short_url_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.add_short_urlBtn, timeout).click()
    def send_add_short_url_input(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.add_short_url_input, timeout)
        el.clear()
        el.send_keys(text)
    def click_add_short_url_cancel(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.add_short_url_cancel, timeout).click()
    def click_add_short_url_confirm(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.add_short_url_confirm, timeout).click()
    def get_created_short_url(self, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.created_short_url, timeout)
        return el.text.strip()

    # 미리보기
    def wait_preview_img_visible(self, timeout=10):
        return BaseClass.wait_visible(self.driver, self.preview_img, timeout)
    def is_preview_text_contains(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.preview_area, timeout)
        return text in el.text
    def get_preview_url(self, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.preview_url, timeout)
        return el.get_attribute("href").strip()
    def is_preview_url_match(self, timeout=10):
        created = self.get_created_short_url(timeout)
        preview = self.get_preview_url(timeout)
        return created == preview

    # 옵션 설정 서브타이틀
    def wait_sms_subtitle_option_visible(self, timeout=10):
        return BaseClass.wait_visible(self.driver, self.sms_subtitle_option, timeout)
