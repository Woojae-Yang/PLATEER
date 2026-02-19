import time
import os
import pytest
from selenium.common import JavascriptException, WebDriverException, NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PageObjects.SegmentPage import SegmentPage
from utilities.BaseClass import BaseClass
from PageObjects.PushNotiPage import PushNotiPage
from selenium.webdriver.common.keys import Keys


@pytest.mark.usefixtures("login")
class TestCampaignCreate(BaseClass):

    Push_campaign_brower_title = "푸시 알림 캠페인 :: GROOBEE"
    Push_sched_campaign_brower_expect_title = "새로운 캠페인 만들기 :: GROOBEE"  # 푸시 알림 캠페인
    Push_sched_campaign_regist_title = "새로운 푸시 알림 캠페인 만들기" # 기본 설정
    Push_sched_campaign_name ="[HS] 푸시_스케쥴_세그먼트_단일발송 테스트 캠페인"
    Push_sched_expected_campaign_name = "[HS] 푸시_스케쥴_세그먼트_단일발송 테스트 캠페인"
    pushNoti_expected_title = "푸시 알림 캠페인"
    Push_sched_campaign_des = "세그먼트:회원ID_광고성,기본 및 본문 이미지, 딥링크, 고급 옵션"
    tag_input = "Automation"
    Push_sched_message_title = "푸시 알림 캠페인"
    Push_sched_message_contents = "내용: 스케쥴 발송 테스트"
    Push_sched_unsubscribe_notice ="[자동화]수신거부070"
    Offsite_seg_id = "[QA][HS] OFFSITE_회원ID_세그먼트용" #qa_hs_seg
    expected_file_name = "pushNoti_test_img.jpg"
    Offsite_deepLink_AOS ="groobee://campaign/detail?id=12"
    Offsite_deepLink_iOS ="https://app.groobee.io/campaign/detail?id=45"
    Offsite_advanced_key ="누텔라"
    Offsite_advanced_value = "15000"

    #타겟팅 유형> 세그먼트, 광고성, 기본 이미지> 설정(업로드된 상태), 본문 이미지,
    # 딥링크(aos,ios), 고급 옵션

    @pytest.mark.case_id(7000)
    def test_7000(self,driver):
        groobee = PushNotiPage(driver)

        # 1. 푸시 알림 캠페인 LNB 클릭
        groobee.click_pushnoti_menu()
        time.sleep(3)

        # 1. 푸시 알림 캠페인 페이지 노출 확인 _브라우저 타이틀
        assert driver.title == self.Push_campaign_brower_title

        campaign_name = "[HS] 푸시_스케쥴_세그먼트_단일발송 테스트 캠페인"
        try:
            groobee.click_play_icon_by_name(cam_name=campaign_name)

            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located(groobee.dialog_confirm_button)
            )

            groobee.click_dialog_confirm_button()

        except TimeoutException:
            print("재생 중인 캠페인이 없어 다이얼로그 없음 → PASS")

    @pytest.mark.case_id(7001)
    def test_7001(self,driver):
        groobee = PushNotiPage(driver)
        # 1.만들기 버튼 클릭
        groobee.click_create_pushnoti_btn()
        time.sleep(2)

        # 2.스케쥴 발송 선택
        groobee.click_create_btn_push_schedule()
        time.sleep(1)

        # 2. 새로운 푸시 알림 캠페인 만들기 페이지 노출 확인
        assert driver.title == self.Push_sched_campaign_brower_expect_title
        time.sleep(1)

    @pytest.mark.case_id(7002)
    def test_7002(self,driver):
        groobee = PushNotiPage(driver)

        # 1. 캠페인명/상세 설명 텍스트필드 입력
        groobee.send_cam_name(self.Push_sched_campaign_name)
        groobee.send_cam_des(self.Push_sched_campaign_des)
        time.sleep(1)

        # 1. 캠페인명/상세 설명 텍스트필드 노출 확인
        assert groobee.get_cam_name() == self.Push_sched_campaign_name
        assert groobee.get_cam_des() == self.Push_sched_campaign_des

    @pytest.mark.case_id(7003)
    def test_7003(self,driver):
        groobee = PushNotiPage(driver)

        # 1. 태그 추가 버튼 클릭
        groobee.click_addtag_btn()

        # 1-1. 엔터로 텍스트필드 태그 입력
        groobee.send_tag_input(self.tag_input)
        # 1-2. 추가 버튼 클릭
        groobee.click_tag_add()

        # 1-2. 태그 노출 확인
        assert groobee.wait_tag_visible(self.tag_input)

    @pytest.mark.case_id(7004)
    def test_7004(self,driver):
        groobee = PushNotiPage(driver)

        # 1. 타겟팅 유형 > 세그먼트 클릭
        groobee.click_type_segment()
        time.sleep(1)
        # 2. 세그먼트 불러오기 RNB 선택
        groobee.click_seg_load()
        time.sleep(1)
        # 2-1. 세그먼트 탭
        groobee.click_seg_tab()
        time.sleep(1)
        # 2-2. 검색 > 세그먼트 입력
        groobee.send_seg_input(self.Offsite_seg_id)
        time.sleep(1)
        # 2-3. 검색된 세그먼트 리스트에서 [0] 클릭
        seg_list = groobee.get_seg_list()
        assert len(seg_list) > 0, "세그먼트 미노출"
        groobee.click_first_seg()
        time.sleep(1)
        # 2-4. 선택 버튼 클릭
        groobee.click_select_btn()
        # 2-5. [다음 단계] 버튼
        groobee.click_next_btn()
        time.sleep(1)

    @pytest.mark.case_id(7005)
    def test_7005(self,driver):
        groobee = PushNotiPage(driver)

        # 1. step 2 예상 타겟 수
        try:
            groobee.click_target_pushnoti_num_btn()
        except TimeoutException:
            driver.save_screenshot("target_result_timeout.png")
            assert False, "예상 타겟 수 결과 UI가 20초 내 노출되지 않음"
        # 1. 다시 확인하기 버튼 노출 확인
        assert groobee.wait_target_num_re_btn_visible()


        # 2. 메시지 작성 > 제목* 입력
        groobee.click_message_title()
        groobee.send_message_title(self.Push_sched_message_title)
        time.sleep(1)

        # 3. 메시지 작성 > 내용* 입력
        groobee.click_message_content()
        groobee.send_message_contests(self.Push_sched_message_contents)
        time.sleep(1)

        # 4. 수신 거부 내용 클릭 > 입력
        groobee.click_unsubscribe_notice()
        time.sleep(1)
        groobee.send_unsubscribe_notice(self.Push_sched_unsubscribe_notice)
        time.sleep(1)

        # 2. 미리 보기 > 제목* 입력 내용 일치 확인
        assert groobee.preview_title_by_text(self.Push_sched_message_title)

        # 3. 미리 보기 > 내용* 입력값 일치
        groobee.assert_push_preview_message(self.Push_sched_message_contents)

        # 4. 미리 보기 > 수신거부 내용 일치
        groobee.assert_push_preview_unsubscribe(self.Push_sched_unsubscribe_notice)

        # 5. 기본 이미지 > 설정 체크
        btn = BaseClass.wait_visible(driver, groobee.default_img_setting, 10)
        groobee.scroll_to(btn)
        time.sleep(1)

        # 6. 본문 이미지 > 파일 업로드
        groobee.click_file_upload_btn()
        time.sleep(1)
        # 6-1. 이미지 넣기
        file_path = BaseClass.getdata_file(self.expected_file_name)
        groobee.send_file_input(file_path)
        time.sleep(1)
        # 6-2. [확인] 버튼
        groobee.click_done_btn_pushnoti()
        time.sleep(1)
        # 6-1. 파일 업로드 일치
        groobee.assert_uploaded_body_image_file_name(self.expected_file_name)
        time.sleep(1)

        # 7. 딥 링크 라디오 버튼 클릭
        groobee.click_deepLink()
        time.sleep(1)
        # 7-1. AOS* > 내용 입력
        groobee.send_deepLink_testArea_AOS(self.Offsite_deepLink_AOS)
        time.sleep(1)
        # 7-2. iOS* > 내용 입력
        groobee.send_deepLink_testArea_iOS(self.Offsite_deepLink_iOS)
        time.sleep(1)

        # 7-1. AOS > 입력 내용 일치
        groobee.assert_deepLink_textArea_AOS(self.Offsite_deepLink_AOS)
        # 7-2. iOS > 입력 내용 일치
        groobee.assert_deepLink_textArea_iOS(self.Offsite_deepLink_iOS)

        # 8. 고급 옵션
        groobee.click_advanced_options()
        time.sleep(1)
        groobee.click_advanced_options_key(self.Offsite_advanced_key)
        time.sleep(1)
        groobee.click_advanced_options_value(self.Offsite_advanced_value)
        time.sleep(1)

        # 8. 고급 옵션 검증
        groobee.assert_advanced_options_key(self.Offsite_advanced_key)
        time.sleep(1)
        groobee.assert_advanced_options_value(self.Offsite_advanced_value)
        time.sleep(1)

    @pytest.mark.case_id(7006)
    def test_7006(self,driver):
        groobee = PushNotiPage(driver)

        # 1. 다음 단계
        groobee.click_next_btn()
        time.sleep(1)

        # 1. 옵션 설정 > 검증
        def assert_send_type_options_exist(self):
            single_option = self.driver.find_elements(*self.send_type_single)
            repeat_option = self.driver.find_elements(*self.send_type_repeat)

            assert len(single_option) > 0, "[FAIL] '단일 발송' 옵션이 존재하지 않습니다."
            assert len(repeat_option) > 0, "[FAIL] '반복 발송' 옵션이 존재하지 않습니다."

        # 1-1. 3단계 - 단일 발송 선택
        groobee.click_send_type_single()
        time.sleep(1)

        #저장하기
        groobee.click_save_btn()
        time.sleep(1)

        #캠페인 저장 - 다이얼로그 노출 > 확인 버튼
        groobee.click_dialog_confirm_button()
        time.sleep(2)


        # 푸시알림 캠페인 LNB
        groobee.click_pushnoti_menu()
        time.sleep(1)

        cam = groobee.get_cam_list_items(self.Push_sched_campaign_name)
        assert cam, \
            f"생성된 캠페인이 리스트에 노출되지 않음: {self.Push_sched_campaign_name}"

        groobee.click_pause_icon_by_name(self.Push_sched_campaign_name)
        time.sleep(1)

        #다이얼로그 캠페인 진행
        groobee.click_dialog_confirm_button()
        time.sleep(2)

        # 2) 캠페인명 검색
        groobee.click_campaign_search()
        time.sleep(1)

        groobee.send_campaign_search(self.Push_sched_campaign_name)
        time.sleep(2)

        # 2-1) 캠페인명 검색 일치 검증
        groobee.search_campaign_row_by_name(self.Push_sched_campaign_name)



        time.sleep(1)



        #2-2) 재생 버튼 클릭 > 캠페인 발송 일시 일치 확인


        # #타겟팅 유형> 세그먼트, 광고성, 기본 이미지> 설정(업로드된 상태), 본문 이미지,
        # 웹브라우저, 고급 옵션
