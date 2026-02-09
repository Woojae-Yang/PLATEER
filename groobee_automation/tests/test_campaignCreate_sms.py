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
    expect_target_text = "예상 타겟 수는"
    expect_sms_msg_subtitle = "메시지 작성"
    contents_input = "자동화 내용 입력"
    personal = "운영테스트"
    personal_input = "대체 발송 입력"
    personal_key = "automation_testing"
    url_input = "https://groobee.shop/"
    expect_sms_option_subtitle = "스케줄"

    @pytest.mark.case_id(16658)
    def test_campaign_create_sms(self, driver, clear_campaigns):
        groobee = SmsPage(driver)

        # 1. SMS 캠페인 LNB 클릭
        groobee.click_sms_menu()

        # 1. SMS 캠페인 페이지 노출 확인
        assert driver.title == self.expect_sms_title

        # ----------------------------------------

        clear_campaigns(groobee)

        # 1. 만들기 버튼 클릭
        groobee.click_create_btn()

        # 1. 새로운 SMS 캠페인 만들기 페이지 노출 확인
        assert driver.title == self.expect_sms_regist_title

        # ----------------------------------------

        # 1. 캠페인명 텍스트필드에 {sms_campaign_input} 입력
        groobee.send_cam_name(self.sms_campaign_input)
        # 2. 상세 설명 텍스트필드에 {sms_des_input} 입력
        groobee.send_cam_des(self.sms_des_input)

        # 1. 캠페인명/상세 설명 텍스트필드 > {sms_campaign_input}/{sms_des_input} 노출 확인

        # ----------------------------------------

        # 1. 태그 추가 버튼 클릭
        # 2. 엔터로 복수 입력 가능 텍스트필드에 {tag_input} 입력
        # 3. ENTER 키 입력
        # 4. 추가 버튼 클릭

        # 1. {tag_input} 노출 확인

        # ----------------------------------------

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

        # 1. 예상 타겟 수 > 확인하기 버튼 활성화 상태 확인

        # ----------------------------------------

        # 1. 확인하기 버튼 클릭
        groobee.click_target_num_btn()

        # 1. {expect_target_text} 노출 확인

        # ----------------------------------------

        # 1. 다음 단계 버튼 클릭
        groobee.click_next_btn()

        # 1. 메시지 설정 화면 노출 확인
        # - expect_sms_msg_subtitle : 메시지 작성

        # ----------------------------------------

        # 1. 내용 텍스트필드에 {contents_input} 입력
        groobee.send_contents_input(self.contents_input)

        # 1. 미리보기 > {contents_input} 노출 확인

        # ----------------------------------------

        # 1. 개인화 변수 추가 버튼 클릭
        # 2. {personal} 개인화 변수 선택
        # 3. 대체 발송 값 텍스트필드에 {personal_input} 입력
        # 4. 확인 버튼 클릭

        # 1. 미리보기 > {personal_key} 노출 확인

        # ----------------------------------------

        # 1. 추가 버튼 클릭
        # 2. URL 입력 텍스트필드에 {url_input} 입력
        # 3. 확인 버튼 클릭
        # 4. 단축 URL 복사 아이콘 클릭
        # 5. 내용 텍스트필드에 붙여넣기 시도 (\n)

        # 1. 미리보기 > 단축 URL 노출 확인

        # ----------------------------------------

        # 1. 파일 업로드 버튼 클릭
        groobee.click_file_upload_btn()
        # 2. TestImage.jpg 업로드 시도
        groobee.send_file_input("TestImage.jpg")
        # 3. 확인 버튼 클릭
        groobee.click_done_btn()

        # 1. 미리보기 > TestImage.jpg 노출 확인 (<img>)

        # ----------------------------------------

        # 1. 다음 단계 버튼 클릭
        groobee.click_next_btn()

        # 1. 옵션 설정 화면 노출
        # - expect_sms_option_subtitle : 스케줄

        # ----------------------------------------

        # 1. 저장 버튼 클릭
        groobee.click_save_btn()
        # 2. 확인 버튼 클릭
        groobee.click_done_btn()

        # 1. SMS 캠페인 페이지 노출 AND 캠페인 리스트 > {sms_campaign_input} 노출 확인
        # - expect_sms_title : SMS 캠페인 :: GROOBEE