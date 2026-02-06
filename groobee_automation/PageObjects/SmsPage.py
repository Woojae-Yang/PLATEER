import time

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
    qa_gp_seg = (By.XPATH, "//h6[contains(text(),'[QA][GP] 세그먼트용')]")

    # 내용 입력
    contents_input = (By.XPATH, "//div[@id='sms-text-content']")

    # -------------------------동작 선언 영역-------------------------
    # 세그먼트 불러오기 RNB(설정할 값 실제 작성)
    def click_qa_gp_seg(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.qa_gp_seg, timeout).click()

    # 내용 입력
    def send_contents_input(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.contents_input, timeout)
        el.clear()
        el.send_keys(text)
