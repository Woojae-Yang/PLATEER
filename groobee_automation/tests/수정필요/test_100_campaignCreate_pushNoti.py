import time
import os
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PageObjects.SegmentPage import SegmentPage
from utilities.BaseClass import BaseClass
from PageObjects.PushNotiPage import PushNotiPage


class TestCampaignCreate(BaseClass):

    Push_sched_campaign_expect_title = "새로운 캠페인 만들기 :: GROOBEE"  # 푸시 알림 캠페인
    Push_sched_campaign_name ="[QA] 푸시_스케쥴_세그먼트_단일발송 테스트 캠페인"
    Push_sched_campaign_des = "세그먼트:회원ID_광고성,기본 및 본문 이미지, 딥링크, 고급 옵션"
    Push_sched_message_title = "푸시 알림 캠페인"
    Push_sched_message_contents = "내용: 스케쥴 발송 테스트"
    Push_sched_unsubscribe_notice ="[자동화]수신거부070"
    Offsite_seg_id = "[QA][HS] OFFSITE_회원ID_세그먼트용" #qa_hs_seg
    Offsite_deepLink_AOS ="groobee://campaign/detail?id=12"
    Offsite_deepLink_iOS ="https://app.groobee.io/campaign/detail?id=45"
    Offsite_advanced_key ="누텔라"
    Offsite_advanced_value = "15000"

    #타겟팅 유형> 세그먼트, 광고성, 기본 이미지> 설정(업로드된 상태), 본문 이미지,
    # 딥링크(aos,ios), 고급 옵션
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
        assert driver.title ==self.Push_sched_campaign_expect_title, f"현재 페이지: {driver.title}, 기대 페이지: {self.Push_sched_campaign_expect_title}"

        #캠페인명/상세 설명 입력
        groobee.send_cam_name().send_keys(self.Push_sched_campaign_name)
        groobee.send_cam_des().send_keys(self.Push_sched_campaign_des)
        time.sleep(1)

        #타겟팅 유형 설정
        groobee.click_type_segment.click()
        time.sleep(1)

        #세그먼트 불러오기 RNB (단일): 버튼 > 세그 탭 > 검색
        groobee.click_seg_load()
        groobee.click_seg_tab()
        #검색 > 세그먼트 입력
        groobee.send_seg_input(self.Offsite_seg_id)
        # 세그먼트 리스트에서 [0] 클릭
        seg_list = groobee.click_qa_hs_seg()
        try:
            assert len(seg_list) > 0, "세그먼트 미노출"
        except AssertionError:
            log.error("세그먼트 미노출")
            raise
        else:
            seg_list[0].click()
        time.sleep(1)

        groobee.click_select_btn().click()
        time.sleep(1)

        # [다음 단계] 버튼
        next_btn = groobee.click_next_btn()
        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(1)

        # 2단계 > 메시지 설정
        #광고성 클릭
        groobee.click_ad_type().click()
        time.sleep(1)

        #예상 타겟 수
        groobee.target_numBtn.click()
        time.sleep(1)

        #메시지 작성 > 제목, 내용 , 수신거부 표기
        groobee.send_message_title().send_keys(self.Push_sched_message_title)
        groobee.send_message_contests().send_keys(self.Push_sched_message_contents)
        time.sleep(1)
        groobee.send_unsubscribe_notice().send_keys(self.Push_sched_unsubscribe_notice)
        time.sleep(1)

        #기본 이미지 > 설정 체크
        groobee.click_default_img_setting().click()
        #본문 이미지 > 파일 업로드
        groobee.click_file_upload_btn().click()
        time.sleep(1)
        # 이미지 넣기
        file_path = BaseClass.getdata_file("HS_TestImage.jpg")
        groobee.send_file_input(file_path)
        time.sleep(1)

        # [확인] 버튼
        groobee.click_done_btn().click()
        time.sleep(1)

        #딥 링크 클릭
        groobee.click_deepLink().click()
        time.sleep(1)
        #aos
        groobee.send_deepLink_testArea_AOS().send_keys(self.Offsite_deepLink_AOS)
        time.sleep(1)
        #ios
        groobee.send_deepLink_testArea_iOS().send_keys(self.Offsite_deepLink_iOS)
        time.sleep(1)

        #고급 옵션!!
        groobee.click_advanced_options().click()
        time.sleep(1)
        groobee.click_advanced_options_key().send_keys(self.Offsite_advanced_key)
        time.sleep(1)
        groobee.click_advanced_options_value().send_keys(self.Offsite_advanced_value)
        time.sleep(1)

        #다음 단계
        next_btn = groobee.click_next_btn()
        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(1)
        #3단계 - 단일 발송

        # #타겟팅 유형> 세그먼트, 광고성, 기본 이미지> 설정(업로드된 상태), 본문 이미지,
        # 딥링크(aos,ios), 고급 옵션
