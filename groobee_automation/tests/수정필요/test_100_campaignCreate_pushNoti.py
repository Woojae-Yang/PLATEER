import time
import os
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PageObjects.SegmentPage import SegmentPage
from utilities.BaseClass import BaseClass
from PageObjects.PushNotiPage import PushNotiPage


class TestCampaignCreate(BaseClass):
    campaign_expect_title = "새로운 캠페인 만들기 :: GROOBEE" #푸시 알림 캠페인
    campain_name ="[QA] 오프사이트-과거-회원ID 테스트 캠페인"
    campaign_des = "오프사이트-과거-회원ID"
    campaign_title = "푸시 알림 캠페인"
    campaign_contents= "내용: 스케쥴 발송 테스트"


    def test_campaign_create_pushNoti(self, driver):
        log = self.get_log()

        groobee = PushNotiPage(driver)

        #푸시 알림 캠페인 메뉴 진입
        groobee. click_pushnoti_menu().click()
        time.sleep(1)

        #만들기 버튼 클릭
        groobee.click_create_btn().click()
        time.sleep(1)

        #스케쥴 발송 선택
        groobee.click_create_btn_push_schedule().click()
        time.sleep(1)

        #타이틀 노출까지 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(PushNotiPage.schedule_cam_title)
        )
        assert driver.title ==self.campaign_expect_title, f"현재 페이지: {driver.title}, 기대 페이지: {self.campaign_expect_title}"