import pytest

from PageObjects.SmsPage import SmsPage
from utilities.BaseClass import BaseClass

@pytest.mark.usefixtures("login")
class TestSmsCampaignCreate:
    campaign_input = "[QA][GP] sms캠페인"
    des_input = "[QA][GP] sms캠페인_상세 설명"
    seg_name = "[QA][GP] 세그먼트용"
    contents_input = "자동화내용입력"

    @pytest.mark.case_id(16658)
    def test_campaign_create_sms(self, driver, clear_campaigns):
        groobee = SmsPage(driver)

        # SMS 캠페인 메뉴 진입
        groobee.click_sms_menu()
        clear_campaigns(groobee)

        # 만들기 버튼 클릭
        groobee.click_create_btn()

        # 캠페인명/상세 설명 입력
        groobee.send_cam_name(self.campaign_input)
        groobee.send_cam_des(self.des_input)

        # 세그먼트 불러오기 RNB
        groobee.click_seg_load()
        groobee.click_seg_tab()
        groobee.send_seg_input(self.seg_name)
        groobee.click_qa_gp_seg()
        groobee.click_select_btn()

        # 예상 타겟 수
        groobee.click_target_num_btn()

        # 다음 단계
        groobee.click_next_btn()

        # 내용
        groobee.send_contents_input(self.contents_input)

        # 파일 업로드 RNB
        groobee.click_file_upload_btn()

        # 파일 업로드
        file_path = BaseClass.getdata_file("TestImage.jpg")
        groobee.send_file_input(file_path)

        # 파일 업로드 RNB 닫기
        groobee.click_done_btn()

        # 다음 단계
        groobee.click_next_btn()

        # 저장
        groobee.click_save_btn()
        groobee.click_done_btn()