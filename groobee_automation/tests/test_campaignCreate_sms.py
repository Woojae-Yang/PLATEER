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

    @pytest.mark.case_id(16658)
    def test_16658(self, driver):
        groobee = SmsPage(driver)

        # 1. SMS 캠페인 LNB 클릭
        groobee.click_sms_menu()

        # 1. SMS 캠페인 페이지 노출 확인
        assert driver.title == self.expect_sms_title

    @pytest.mark.case_id(16659)
    def test_16659(self, driver, clear_campaigns):
        groobee = SmsPage(driver)
        clear_campaigns(groobee)

        # 1. 만들기 버튼 클릭
        groobee.click_create_btn()

        # 1. 새로운 SMS 캠페인 만들기 페이지 노출 확인
        assert driver.title == self.expect_sms_regist_title

    @pytest.mark.case_id(16660)
    def test_16660(self, driver):
        groobee = SmsPage(driver)

        # 1. 캠페인명 텍스트필드에 {sms_campaign_input} 입력
        groobee.send_cam_name(self.sms_campaign_input)
        # 2. 상세 설명 텍스트필드에 {sms_des_input} 입력
        groobee.send_cam_des(self.sms_des_input)

        # 1. 캠페인명 텍스트필드 > {sms_campaign_input} 노출 확인
        assert groobee.get_cam_name() == self.sms_campaign_input
        # 2. 상세 설명 텍스트필드 > {sms_des_input} 노출 확인
        assert groobee.get_cam_des() == self.sms_des_input

    @pytest.mark.case_id(16661)
    def test_16661(self, driver):
        groobee = SmsPage(driver)

        # 1. 태그 추가 버튼 클릭
        groobee.click_addtag_btn()
        # 2. 엔터로 복수 입력 가능 텍스트필드에 {tag_input} 입력
        groobee.send_tag_input(self.tag_input)
        # 3. 추가 버튼 클릭
        groobee.click_tag_add()

        # 3. {tag_input} 노출 확인
        assert groobee.wait_tag_visible(self.tag_input)

    @pytest.mark.case_id(16662)
    def test_16662(self, driver):
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

    @pytest.mark.case_id(16663)
    def test_16663(self, driver):
        groobee = SmsPage(driver)

        # 1. 확인하기 버튼 클릭
        groobee.click_target_num_btn()

        # 1. 다시 확인하기 버튼 노출 확인
        assert groobee.wait_target_num_re_btn_visible()

    @pytest.mark.case_id(16664)
    def test_16664(self, driver):
        groobee = SmsPage(driver)

        # 1. 다음 단계 버튼 클릭
        groobee.click_next_btn()

        # 1. 메시지 설정 화면 노출 확인
        assert groobee.wait_sms_subtitle_msg_visible()

    @pytest.mark.case_id(16665)
    def test_16665(self, driver):
        groobee = SmsPage(driver)

        # 1. 내용 텍스트필드에 {contents_input} 입력
        groobee.send_contents_input(self.contents_input)

        # 1. 미리보기 > {contents_input} 노출 확인
        assert groobee.is_preview_text_contains(self.contents_input)

    @pytest.mark.case_id(16666)
    def test_16666(self, driver):
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

    @pytest.mark.case_id(16667)
    def test_16667(self, driver):
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

    @pytest.mark.case_id(16668)
    def test_16668(self, driver):
        groobee = SmsPage(driver)

        # 1. 파일 업로드 버튼 클릭
        groobee.click_file_upload_btn()
        # 2. TestImage.jpg 업로드 시도
        groobee.send_file_input("TestImage.jpg")
        # 3. 확인 버튼 클릭
        groobee.click_done_btn()

        # 3. 미리보기 > TestImage.jpg 노출 확인
        assert groobee.is_preview_img_visible()

    @pytest.mark.case_id(16669)
    def test_16669(self, driver):
        groobee = SmsPage(driver)

        # 1. 다음 단계 버튼 클릭
        groobee.click_next_btn()

        # 1. 옵션 설정 화면 노출 확인
        assert groobee.wait_sms_subtitle_option_visible()

    @pytest.mark.case_id(16670)
    def test_16670(self, driver):
        groobee = SmsPage(driver)

        # 1. 저장 버튼 클릭
        groobee.click_save_btn()
        # 2. 확인 버튼 클릭
        groobee.click_done_btn()

        # 2. 캠페인 리스트 > {sms_campaign_input} 노출 확인
        assert groobee.get_cam_list_item(self.sms_campaign_input).is_displayed()

    @pytest.mark.case_id(16671)
    def test_16671(self, driver):
        groobee = SmsPage(driver)

        # 1. 관리 도구 클릭
        groobee.click_tools_icon_by_name(self.sms_campaign_input)
        # 2. 수정 클릭
        groobee.click_modify_icon()

        # 2. SMS 캠페인 수정하기 페이지 노출 확인
        assert driver.title == self.expect_sms_modify_title

    @pytest.mark.case_id(16672)
    def test_16672(self, driver):
        groobee = SmsPage(driver)

        # 1. 캠페인명 텍스트필드에 {sms_campaign_modify_input} 입력
        groobee.send_cam_name(self.sms_campaign_modify_input)

        # 1. 캠페인명 텍스트필드 > {sms_campaign_modify_input} 노출 확인
        assert groobee.get_cam_name() == self.sms_campaign_modify_input

    @pytest.mark.case_id(16673)
    def test_16673(self, driver):
        groobee = SmsPage(driver)

        # 1. 확인하기 버튼 클릭
        groobee.click_target_num_btn()

        # 1. 다시 확인하기 버튼 노출 확인
        assert groobee.wait_target_num_re_btn_visible()

    @pytest.mark.case_id(16674)
    def test_16674(self, driver):
        groobee = SmsPage(driver)

        # 1. 다음 단계 버튼 클릭
        groobee.click_next_btn()

        # 1. 메시지 설정 화면 노출 확인
        assert groobee.wait_sms_subtitle_msg_visible()

    @pytest.mark.case_id(16675)
    def test_16675(self, driver):
        groobee = SmsPage(driver)

        # 1. 내용 텍스트필드에 {contents_modify_input} 입력
        groobee.send_contents_input(self.contents_modify_input)

        # 1. 미리보기 > {contents_modify_input} 노출 확인
        assert groobee.is_preview_text_contains(self.contents_modify_input)

    @pytest.mark.case_id(16676)
    def test_16676(self, driver):
        groobee = SmsPage(driver)

        # 1. 다음 단계 버튼 클릭
        groobee.click_next_btn()

        # 1. 옵션 설정 화면 노출 확인
        assert groobee.wait_sms_subtitle_option_visible()

    @pytest.mark.case_id(16677)
    def test_16677(self, driver):
        groobee = SmsPage(driver)

        # 1. 저장 버튼 클릭
        groobee.click_save_btn()
        # 2. 확인 버튼 클릭
        groobee.click_done_btn()

        # 2. 캠페인 리스트 > {sms_campaign_modify_input} 노출 확인
        assert groobee.get_cam_list_item(self.sms_campaign_modify_input).is_displayed()