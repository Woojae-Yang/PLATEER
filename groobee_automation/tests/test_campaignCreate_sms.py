import pytest

from PageObjects.SmsPage import SmsPage

@pytest.mark.usefixtures("login")
class TestSmsCampaignCreate:
    expect_sms_title = "SMS 캠페인 :: GROOBEE"
    expect_sms_regist_title = "새로운 SMS 캠페인 만들기 :: GROOBEE"
    sms_campaign_input = "[QA][GP][Auto] SMS 캠페인"
    sms_des_input = "[QA][GP][Auto] SMS 캠페인_상세 설명"
    tag_input = "자동화 태그"
    seg_input = "[QA][GP][Auto] 세그먼트"
    contents_input = "자동화 내용 입력"
    personal_input = "대체 발송 입력"
    personal_key = "automation_testing"
    url_input = "https://groobee.shop/"
    expect_sms_modify_title = "SMS 캠페인 수정하기 :: GROOBEE"
    sms_campaign_modify_input = "[QA][GP][Auto] SMS 캠페인_수정"
    contents_modify_input = "_수정"
    expect_copy_text = "-COPY"
    sms_campaign_copy_input = "[QA][GP][Auto] SMS 캠페인_복사"
    contents_copy_input = "_복사"
    automation_text = "[Auto]"
    sms_campaign_repeat_input = "[QA][GP][Auto] SMS 캠페인_반복 발송"
    expect_repeat_cycle_text = "1일마다"

    @pytest.mark.case_id(17208)
    def test_17208(self, driver):
        groobee = SmsPage(driver)

        # 1. SMS 캠페인 LNB 클릭
        groobee.click_sms_menu()

        # 1. SMS 캠페인 페이지 노출 확인
        assert driver.title == self.expect_sms_title

    @pytest.mark.case_id(17209)
    def test_17209(self, driver, clear_campaigns):
        groobee = SmsPage(driver)
        clear_campaigns(groobee)

        # 1. 만들기 버튼 클릭
        groobee.click_create_btn()

        # 1. 새로운 SMS 캠페인 만들기 페이지 노출 확인
        assert driver.title == self.expect_sms_regist_title

    @pytest.mark.case_id(17210)
    def test_17210(self, driver):
        groobee = SmsPage(driver)

        # 1. 캠페인명 텍스트필드에 {sms_campaign_input} 입력
        groobee.send_cam_name(self.sms_campaign_input)
        # 2. 상세 설명 텍스트필드에 {sms_des_input} 입력
        groobee.send_cam_des(self.sms_des_input)

        # 1. 캠페인명 텍스트필드 > {sms_campaign_input} 노출 확인
        assert groobee.get_cam_name() == self.sms_campaign_input
        # 2. 상세 설명 텍스트필드 > {sms_des_input} 노출 확인
        assert groobee.get_cam_des() == self.sms_des_input

    @pytest.mark.case_id(17211)
    def test_17211(self, driver):
        groobee = SmsPage(driver)

        # 1. 태그 추가 버튼 클릭
        groobee.click_addtag_btn()
        # 2. 엔터로 복수 입력 가능 텍스트필드에 {tag_input} 입력
        groobee.send_tag_input(self.tag_input)
        # 3. 추가 버튼 클릭
        groobee.click_tag_add()

        # 3. {tag_input} 노출 확인
        assert groobee.wait_tag_visible(self.tag_input)

    @pytest.mark.case_id(17212)
    def test_17212(self, driver):
        groobee = SmsPage(driver)

        # 1. 세그먼트 불러오기 버튼 클릭
        groobee.click_seg_load()
        # 2. 세그먼트 탭 선택
        groobee.click_seg_tab()
        # 3. 세그먼트명 검색 텍스트필드에 {seg_input} 입력
        groobee.send_seg_input(self.seg_input)
        # 4. {seg_input} 리스트 클릭
        groobee.click_qa_gp_seg()
        # 5. 선택 버튼 클릭
        groobee.click_select_btn()

        # 5. 예상 타겟 수 > 확인하기 버튼 활성화 상태 확인
        assert groobee.wait_target_num_btn_clickable()

    @pytest.mark.case_id(17213)
    def test_17213(self, driver):
        groobee = SmsPage(driver)

        # 1. 확인하기 버튼 클릭
        groobee.click_target_num_btn()

        # 1. 다시 확인하기 버튼 노출 확인
        assert groobee.wait_target_num_re_btn_visible()

    @pytest.mark.case_id(17214)
    def test_17214(self, driver):
        groobee = SmsPage(driver)

        # 1. 다음 단계 버튼 클릭
        groobee.click_next_btn()

        # 1. 메시지 설정 화면 노출 확인
        assert groobee.wait_sms_subtitle_msg_visible()

    @pytest.mark.case_id(17215)
    def test_17215(self, driver):
        groobee = SmsPage(driver)

        # 1. 내용 텍스트필드에 {contents_input} 입력
        groobee.send_contents_input(self.contents_input)

        # 1. 미리보기 > {contents_input} 노출 확인
        assert groobee.is_preview_text_contains(self.contents_input)

    @pytest.mark.case_id(17216)
    def test_17216(self, driver):
        groobee = SmsPage(driver)

        # 1. 개인화 변수 추가 버튼 클릭
        groobee.click_add_personal_btn()
        # 2. {personal} 개인화 변수 선택
        groobee.click_add_personal_cbx()
        groobee.click_add_personal_auto()
        # 3. 대체 발송 값 텍스트필드에 {personal_input} 입력
        groobee.send_add_personal_input(self.personal_input)
        # 4. 확인 버튼 클릭
        groobee.click_add_personal_confirm()

        # 4. 미리보기 > {personal_key} 노출 확인
        assert groobee.is_preview_text_contains(self.personal_key)

    @pytest.mark.case_id(17217)
    def test_17217(self, driver):
        groobee = SmsPage(driver)

        # 1. 추가 버튼 클릭
        groobee.click_add_short_url_btn()
        # 2. URL 입력 텍스트필드에 {url_input} 입력
        groobee.send_add_short_url_input(self.url_input)
        # 3. 확인 버튼 클릭
        groobee.click_add_short_url_confirm()
        # 4. 내용 텍스트필드에 단축 URL 입력
        groobee.send_contents_input(groobee.get_created_short_url())

        # 4. 미리보기 > 단축 URL 노출 확인
        assert groobee.is_preview_url_match()

    @pytest.mark.case_id(17218)
    def test_17218(self, driver):
        groobee = SmsPage(driver)

        # 1. 파일 업로드 버튼 클릭
        groobee.click_file_upload_btn()
        # 2. TestImage.jpg 업로드 시도
        groobee.send_file_input("TestImage.jpg")
        # 3. 확인 버튼 클릭
        groobee.click_done_btn()

        # 3. 미리보기 > TestImage.jpg 노출 확인
        assert groobee.is_preview_img_visible()

    @pytest.mark.case_id(17219)
    def test_17219(self, driver):
        groobee = SmsPage(driver)

        # 1. 다음 단계 버튼 클릭
        groobee.click_next_btn()

        # 1. 옵션 설정 화면 노출 확인
        assert groobee.wait_sms_subtitle_option_visible()

    @pytest.mark.case_id(17220)
    def test_17220(self, driver):
        groobee = SmsPage(driver)

        # 1. 발송 일시에 현재 시간 +3분 입력
        groobee.send_date_input(3)

        # 1. 발송 일시 > 현재 시간 +3분 노출 확인
        assert groobee.is_date_input_match(3)

    @pytest.mark.case_id(17221)
    def test_17221(self, driver):
        groobee = SmsPage(driver)

        # 1. 저장 버튼 클릭
        groobee.click_save_btn()
        # 2. 확인 버튼 클릭
        groobee.click_done_btn()

        # 2. 캠페인 리스트 > {sms_campaign_input} 노출 확인
        assert groobee.get_cam_item(self.sms_campaign_input).is_displayed()

    @pytest.mark.case_id(17222)
    def test_17222(self, driver):
        groobee = SmsPage(driver)

        # 1. 만들기 버튼 클릭
        groobee.click_create_btn()

        # 1. 새로운 SMS 캠페인 만들기 페이지 노출 확인
        assert driver.title == self.expect_sms_regist_title

    @pytest.mark.case_id(17223)
    def test_17223(self, driver):
        groobee = SmsPage(driver)

        # 1. 캠페인명 텍스트필드에 {sms_campaign_repeat_input} 입력
        groobee.send_cam_name(self.sms_campaign_repeat_input)
        # 2. 상세 설명 텍스트필드에 {sms_des_input} 입력
        groobee.send_cam_des(self.sms_des_input)

        # 1. 캠페인명 텍스트필드 > {sms_campaign_repeat_input} 노출 확인
        assert groobee.get_cam_name() == self.sms_campaign_repeat_input
        # 2. 상세 설명 텍스트필드 > {sms_des_input} 노출 확인
        assert groobee.get_cam_des() == self.sms_des_input

    @pytest.mark.case_id(17224)
    def test_17224(self, driver):
        groobee = SmsPage(driver)

        # 1. 태그 추가 버튼 클릭
        groobee.click_addtag_btn()
        # 2. 엔터로 복수 입력 가능 텍스트필드에 {tag_input} 입력
        groobee.send_tag_input(self.tag_input)
        # 3. 추가 버튼 클릭
        groobee.click_tag_add()

        # 3. {tag_input} 노출 확인
        assert groobee.wait_tag_visible(self.tag_input)

    @pytest.mark.case_id(17225)
    def test_17225(self, driver):
        groobee = SmsPage(driver)

        # 1. 세그먼트 불러오기 버튼 클릭
        groobee.click_seg_load()
        # 2. 세그먼트 탭 선택
        groobee.click_seg_tab()
        # 3. 세그먼트명 검색 텍스트필드에 {seg_input} 입력
        groobee.send_seg_input(self.seg_input)
        # 4. {seg_input} 리스트 클릭
        groobee.click_qa_gp_seg()
        # 5. 선택 버튼 클릭
        groobee.click_select_btn()

        # 5. 예상 타겟 수 > 확인하기 버튼 활성화 상태 확인
        assert groobee.wait_target_num_btn_clickable()

    @pytest.mark.case_id(17226)
    def test_17226(self, driver):
        groobee = SmsPage(driver)

        # 1. 확인하기 버튼 클릭
        groobee.click_target_num_btn()

        # 1. 다시 확인하기 버튼 노출 확인
        assert groobee.wait_target_num_re_btn_visible()

    @pytest.mark.case_id(17227)
    def test_17227(self, driver):
        groobee = SmsPage(driver)

        # 1. 다음 단계 버튼 클릭
        groobee.click_next_btn()

        # 1. 메시지 설정 화면 노출 확인
        assert groobee.wait_sms_subtitle_msg_visible()

    @pytest.mark.case_id(17228)
    def test_17228(self, driver):
        groobee = SmsPage(driver)

        # 1. 내용 텍스트필드에 {contents_input} 입력
        groobee.send_contents_input(self.contents_input)

        # 1. 미리보기 > {contents_input} 노출 확인
        assert groobee.is_preview_text_contains(self.contents_input)

    @pytest.mark.case_id(17229)
    def test_17229(self, driver):
        groobee = SmsPage(driver)

        # 1. 추가 버튼 클릭
        groobee.click_add_short_url_btn()
        # 2. URL 입력 텍스트필드에 {url_input} 입력
        groobee.send_add_short_url_input(self.url_input)
        # 3. 확인 버튼 클릭
        groobee.click_add_short_url_confirm()
        # 4. 내용 텍스트필드에 단축 URL 입력
        groobee.send_contents_input(groobee.get_created_short_url())

        # 4. 미리보기 > 단축 URL 노출 확인
        assert groobee.is_preview_url_match()

    @pytest.mark.case_id(17230)
    def test_17230(self, driver):
        groobee = SmsPage(driver)

        # 1. 파일 업로드 버튼 클릭
        groobee.click_file_upload_btn()
        # 2. TestImage2.jpg 업로드 시도
        groobee.send_file_input("TestImage2.jpg")
        # 3. 확인 버튼 클릭
        groobee.click_done_btn()

        # 3. 미리보기 > TestImage2.jpg 노출 확인
        assert groobee.is_preview_img_visible()

    @pytest.mark.case_id(17231)
    def test_17231(self, driver):
        groobee = SmsPage(driver)

        # 1. 다음 단계 버튼 클릭
        groobee.click_next_btn()

        # 1. 옵션 설정 화면 노출 확인
        assert groobee.wait_sms_subtitle_option_visible()

    @pytest.mark.case_id(17232)
    def test_17232(self, driver):
        groobee = SmsPage(driver)

        # 1. 반복 발송 클릭
        groobee.click_repeat_btn()
        # 2. 설정하기 버튼 클릭
        groobee.click_cycle_btn()
        # 3. 확인 버튼 클릭
        groobee.click_done_btn()
        # 4. 발송 시간에 현재 시간 +3분 입력
        groobee.send_time_input(3)

        # 3. 반복 주기 > {expect_repeat_cycle_text} 노출 확인
        assert groobee.is_repeat_cycle_text_visible(self.expect_repeat_cycle_text)
        # 4. 발송 시간 > 현재 시간 +3분 노출 확인
        assert groobee.is_time_input_match(3)

    @pytest.mark.case_id(17233)
    def test_17233(self, driver):
        groobee = SmsPage(driver)

        # 1. 저장 버튼 클릭
        groobee.click_save_btn()
        # 2. 확인 버튼 클릭
        groobee.click_done_btn()

        # 2. 캠페인 리스트 > {sms_campaign_repeat_input} 노출 확인
        assert groobee.get_cam_item(self.sms_campaign_repeat_input).is_displayed()

    @pytest.mark.case_id(17234)
    def test_17234(self, driver):
        groobee = SmsPage(driver)

        # 1. 관리 도구 클릭
        groobee.click_tools_icon_by_name(self.sms_campaign_input)
        # 2. 수정 클릭
        groobee.click_modify_icon()

        # 2. SMS 캠페인 수정하기 페이지 노출 확인
        assert driver.title == self.expect_sms_modify_title

    @pytest.mark.case_id(17235)
    def test_17235(self, driver):
        groobee = SmsPage(driver)

        # 1. 캠페인명 텍스트필드에 {sms_campaign_modify_input} 입력
        groobee.send_cam_name(self.sms_campaign_modify_input)

        # 1. 캠페인명 텍스트필드 > {sms_campaign_modify_input} 노출 확인
        assert groobee.get_cam_name() == self.sms_campaign_modify_input

    @pytest.mark.case_id(17236)
    def test_17236(self, driver):
        groobee = SmsPage(driver)

        # 1. 확인하기 버튼 클릭
        groobee.click_target_num_btn()

        # 1. 다시 확인하기 버튼 노출 확인
        assert groobee.wait_target_num_re_btn_visible()

    @pytest.mark.case_id(17237)
    def test_17237(self, driver):
        groobee = SmsPage(driver)

        # 1. 다음 단계 버튼 클릭
        groobee.click_next_btn()

        # 1. 메시지 설정 화면 노출 확인
        assert groobee.wait_sms_subtitle_msg_visible()

    @pytest.mark.case_id(17238)
    def test_17238(self, driver):
        groobee = SmsPage(driver)

        # 1. 내용 텍스트필드에 {contents_modify_input} 입력
        groobee.send_contents_input(self.contents_modify_input)

        # 1. 미리보기 > {contents_modify_input} 노출 확인
        assert groobee.is_preview_text_contains(self.contents_modify_input)

    @pytest.mark.case_id(17239)
    def test_17239(self, driver):
        groobee = SmsPage(driver)

        # 1. 다음 단계 버튼 클릭
        groobee.click_next_btn()

        # 1. 옵션 설정 화면 노출 확인
        assert groobee.wait_sms_subtitle_option_visible()

    @pytest.mark.case_id(17240)
    def test_17240(self, driver):
        groobee = SmsPage(driver)

        # 1. 저장 버튼 클릭
        groobee.click_save_btn()
        # 2. 확인 버튼 클릭
        groobee.click_done_btn()

        # 2. 캠페인 리스트 > {sms_campaign_modify_input} 노출 확인
        assert groobee.get_cam_item(self.sms_campaign_modify_input).is_displayed()

    @pytest.mark.case_id(17241)
    def test_17241(self, driver):
        groobee = SmsPage(driver)

        # 1. 관리 도구 클릭
        groobee.click_tools_icon_by_name(self.sms_campaign_modify_input)
        # 2. 복사 클릭
        groobee.click_copy_icon()

        # 2. 새로운 SMS 캠페인 만들기 페이지 노출 확인
        assert driver.title == self.expect_sms_regist_title
        # 3. 캠페인명 텍스트필드 > {expect_copy_text} 노출 확인
        assert self.expect_copy_text in groobee.get_cam_name()

    @pytest.mark.case_id(17242)
    def test_17242(self, driver):
        groobee = SmsPage(driver)

        # 1. 캠페인명 텍스트필드에 {sms_campaign_copy_input} 입력
        groobee.send_cam_name(self.sms_campaign_copy_input)

        # 1. 캠페인명 텍스트필드 > {sms_campaign_copy_input} 노출 확인
        assert groobee.get_cam_name() == self.sms_campaign_copy_input

    @pytest.mark.case_id(17243)
    def test_17243(self, driver):
        groobee = SmsPage(driver)

        # 1. 확인하기 버튼 클릭
        groobee.click_target_num_btn()

        # 1. 다시 확인하기 버튼 노출 확인
        assert groobee.wait_target_num_re_btn_visible()

    @pytest.mark.case_id(17244)
    def test_17244(self, driver):
        groobee = SmsPage(driver)

        # 1. 다음 단계 버튼 클릭
        groobee.click_next_btn()

        # 1. 메시지 설정 화면 노출 확인
        assert groobee.wait_sms_subtitle_msg_visible()

    @pytest.mark.case_id(17245)
    def test_17245(self, driver):
        groobee = SmsPage(driver)

        # 1. 내용 텍스트필드에 {contents_copy_input} 입력
        groobee.send_contents_input(self.contents_copy_input)

        # 1. 미리보기 > {contents_copy_input} 노출 확인
        assert groobee.is_preview_text_contains(self.contents_copy_input)

    @pytest.mark.case_id(17246)
    def test_17246(self, driver):
        groobee = SmsPage(driver)

        # 1. 다음 단계 버튼 클릭
        groobee.click_next_btn()

        # 1. 옵션 설정 화면 노출 확인
        assert groobee.wait_sms_subtitle_option_visible()

    @pytest.mark.case_id(17247)
    def test_17247(self, driver):
        groobee = SmsPage(driver)

        # 1. 저장 버튼 클릭
        groobee.click_save_btn()
        # 2. 확인 버튼 클릭
        groobee.click_done_btn()

        # 2. 캠페인 리스트 > {sms_campaign_copy_input} 노출 확인
        assert groobee.get_cam_item(self.sms_campaign_copy_input).is_displayed()

    @pytest.mark.case_id(17248)
    def test_17248(self, driver):
        groobee = SmsPage(driver)

        # 1. 단일 발송 탭 클릭
        groobee.click_single_tab()
        # 2. 관리 도구 클릭
        # 3. 완료 탭으로 이동 클릭 (반복)
        groobee.moveto_complete_by_name(self.automation_text)

        # 3. 캠페인 리스트 > [Auto] 캠페인 미노출 확인
        assert not groobee.get_cam_list_items(self.automation_text)

    @pytest.mark.case_id(17249)
    def test_17249(self, driver):
        groobee = SmsPage(driver)

        # 1. 반복 발송 탭 클릭
        groobee.click_repeat_tab()
        # 2. 관리 도구 클릭
        # 3. 완료 탭으로 이동 클릭 (반복)
        groobee.moveto_complete_by_name(self.automation_text)

        # 3. 캠페인 리스트 > [Auto] 캠페인 미노출 확인
        assert not groobee.get_cam_list_items(self.automation_text)

    @pytest.mark.case_id(17250)
    def test_17250(self, driver):
        groobee = SmsPage(driver)

        # 1. 발송 완료 탭 클릭
        groobee.click_complete_tab()
        # 2. 관리 도구 클릭
        # 3. 삭제 클릭
        # 4. 삭제 버튼 클릭 (반복)
        groobee.delete_campaign_by_name(self.automation_text)

        # 4. 캠페인 리스트 > [Auto] 캠페인 미노출 확인
        assert not groobee.get_cam_list_items(self.automation_text)