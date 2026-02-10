import time
import os
import pytest
from selenium.common import JavascriptException, WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PageObjects.SegmentPage import SegmentPage
from utilities.BaseClass import BaseClass
from PageObjects.PushNotiPage import PushNotiPage


@pytest.mark.usefixtures("login")
class TestCampaignCreate(BaseClass):

    Push_sched_campaign_expect_title = "새로운 캠페인 만들기 :: GROOBEE"  # 푸시 알림 캠페인
    Push_sched_campaign_name ="[QA] 푸시_스케쥴_세그먼트_단일발송 테스트 캠페인"
    Push_sched_expected_campaign_name = "[QA] 푸시_스케쥴_세그먼트_단일발송 테스트 캠페인"
    pushNoti_expected_title = "푸시 알림 캠페인"

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
        groobee. click_pushnoti_menu()
        time.sleep(2)

        #만들기 버튼 클릭
        groobee.click_create_btn()
        time.sleep(1)

        #스케쥴 발송 선택
        groobee.click_create_btn_push_schedule()
        time.sleep(1)

        #타이틀 노출까지 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(PushNotiPage.schedule_cam_title)
        )
        assert driver.title ==self.Push_sched_campaign_expect_title, f"현재 페이지: {driver.title}, 기대 페이지: {self.Push_sched_campaign_expect_title}"

        #캠페인명/상세 설명 입력
        groobee.send_cam_name(self.Push_sched_campaign_name)
        groobee.send_cam_des(self.Push_sched_campaign_des)
        time.sleep(1)

        #타겟팅 유형 설정
        groobee.click_type_segment
        time.sleep(1)

        #세그먼트 불러오기 RNB (단일): 버튼 > 세그 탭 > 검색
        groobee.click_seg_load()
        groobee.click_seg_tab()
        #검색 > 세그먼트 입력
        groobee.send_seg_input(self.Offsite_seg_id)
        # 세그먼트 리스트에서 [0] 클릭
        seg_list = groobee.get_seg_list()
        assert len(seg_list) > 0, "세그먼트 미노출"

        groobee.click_first_seg()
        time.sleep(1)

        groobee.click_select_btn()
        time.sleep(1)

        # [다음 단계] 버튼
        groobee.click_next_btn()
        time.sleep(1)

        # 2단계 > 메시지 설정
        #광고성 클릭
        #groobee.click_info_type()
        #time.sleep(1)

        #예상 타겟 수
        try:
            groobee.click_target_pushNoti_num_btn()
        except TimeoutException:
            driver.save_screenshot("target_result_timeout.png")
            assert False, "예상 타겟 수 결과 UI가 20초 내 노출되지 않음"
        ## 예상 타겟 수 > 다시 확인하기 문구 체크
        #target_result

        #메시지 작성 > 제목, 내용 , 수신거부 표기
        groobee.click_message_title()
        time.sleep(1)
        groobee.send_message_title(self.Push_sched_message_title)
        time.sleep(1)

        # 메시지 내용 클릭 > 입력
        groobee.click_message_content()
        time.sleep(1)
        groobee.send_message_contests(self.Push_sched_message_contents)
        time.sleep(1)

        # 수신 거부 내용 클릭 > 입력
        groobee.click_unsubscribe_notice()
        time.sleep(1)
        groobee.send_unsubscribe_notice(self.Push_sched_unsubscribe_notice)
        time.sleep(1)

        # 스크롤 실행
        # 기본 이미지 > 설정 체크
        btn = BaseClass.wait_visible(driver, groobee.default_img_setting, 10)
        groobee.scroll_to(btn)
        time.sleep(1)

        #본문 이미지 > 파일 업로드
        groobee.click_file_upload_btn()
        time.sleep(1)
        # 이미지 넣기
        file_path = BaseClass.getdata_file("HS_TestImage.jpg")
        groobee.send_file_input(file_path)
        time.sleep(1)

        # [확인] 버튼
        groobee.click_done_btn_pushNoti()
        time.sleep(1)

        #딥 링크 클릭
        groobee.click_deepLink()
        time.sleep(1)
        #aos
        groobee.send_deepLink_testArea_AOS().send_keys(self.Offsite_deepLink_AOS)
        time.sleep(1)
        #ios
        groobee.send_deepLink_testArea_iOS().send_keys(self.Offsite_deepLink_iOS)
        time.sleep(1)

        #고급 옵션!
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
        groobee.click_send_type_single().click()
        time.sleep(1)

        #저장하기
        groobee.click_save_btn().click()
        time.sleep(1)

        #캠페인 저장 - 다이얼로그 노출 > 확인 버튼
        groobee.click_dialog_confirm_button().click()
        time.sleep(2)

        # 1) 리스트 > 2)캠페인명 검색  > 노출 확인
        #     Push_sched_campaign_name ="[QA] 푸시_스케쥴_세그먼트_단일발송 테스트 캠페인"
        # 1) 리스트 화면 - 푸시알림 캠페인 확인

        # 페이지 타이틀 일치 확인
        groobee.assert_page_title_matches(
            driver,
            pushNoti_expected_title="푸시 알림 캠페인"
        )
        time.sleep(1)

        # 2) 캠페인명 검색
        groobee.send_campaign_search().clear()
        groobee.send_campaign_search().send_keys(self.Push_sched_campaign_name)
        time.sleep(2)

        # 2-1) 캠페인명 검색 일치 검증
        groobee.assert_searched_campaign_matches(
            driver,
            Push_sched_expected_campaign_name="[QA] 푸시_스케쥴_세그먼트_단일발송 테스트 캠페인"
        )
        time.sleep(1)



        # 재생 버튼 클릭


        # #타겟팅 유형> 세그먼트, 광고성, 기본 이미지> 설정(업로드된 상태), 본문 이미지,
        # 딥링크(aos,ios), 고급 옵션
