import pytest
import time
from PageObjects.OnsitePage import OnsitePage
from PageObjects.CampaignPage import CampaignPage
from utilities.BaseClass import BaseClass


@pytest.mark.usefixtures("login")
class TestCreateCampaign(BaseClass):
    # 테스트 변수 설정
    TEST_TITLE_DATA = "[QA][자동화][PC] 이미지맵"
    TEST_DES_DATA = "[QA][자동화][PC] 이미지맵_상세설명"
    TEST_TAG_DATA = "자동화태그"
    TEST_SEG_DATA = "[QA][JE] 자동화 세그먼트"
    TEST_URL = "https://groobee.shop"
    TEST_TITLE_TXT = "[QA][자동화]타이틀"
    TEST_TXT = "[QA][자동화]내용"
    TEST_BTN_TXT = "[QA]버튼"
    TEST_TIME_NUM = "3"
    TEST_PER_NUM = "80"
    TEST_AREA1_NAME_TXT = "영역1-이름"
    TEST_IMG = "TestImage.png"

    @pytest.mark.case_id(16657)
    def test1(self, driver):
        oncam = OnsitePage(driver)

        oncam.click_menu(oncam.campaignMenu)
        oncam.click_button(oncam.createBtn)
        oncam.click_dropdown(oncam.create_dropdown_onsite)
        assert oncam.is_stepper1(), "[Fail] 만들기 1단계 진입 실패"

    @pytest.mark.case_id(16657)
    def test2(self, driver):
        oncam = OnsitePage(driver)

        oncam.input_text(oncam.campaign_name_input, self.TEST_TITLE_DATA)
        result = (
            oncam.is_campaign_reg_name().get_attribute("value") == self.TEST_TITLE_DATA
        )
        assert result, "[Fail] 캠페인명 입력 실패"

    @pytest.mark.case_id(16657)
    def test3(self, driver):
        oncam = OnsitePage(driver)

        oncam.input_text(oncam.campaign_des_input, self.TEST_DES_DATA)
        result = (
            oncam.is_campaign_reg_des().get_attribute("value") == self.TEST_DES_DATA
        )
        assert result, "[Fail] 상세설명 입력 실패"

    @pytest.mark.case_id(16657)
    def test4(self, driver):
        oncam = OnsitePage(driver)

        oncam.click_button(oncam.tag_btn)
        assert oncam.is_add_tag_modal(), "[Fail] 모달 미노출"

    @pytest.mark.case_id(16657)
    def test5(self, driver):
        oncam = OnsitePage(driver)

        oncam.input_chip(oncam.com_tag_input, self.TEST_TAG_DATA)
        oncam.click_button(oncam.com_tag_add_btn)
        time.sleep(1)
        result = oncam.is_added_tag(self.TEST_TAG_DATA)
        assert result, "[Fail] 태그 추가 실패"

    @pytest.mark.case_id(16657)
    def test6(self, driver):
        oncam = OnsitePage(driver)
        result = oncam.click_access_type(oncam.access_type_pc)
        assert result, "[Fail] 접속 유형 선택 실패"

    @pytest.mark.case_id(16657)
    def test7(self, driver):
        oncam = OnsitePage(driver)

        oncam.click_button(oncam.seg_load)
        oncam.click_tab(oncam.seg_tab)
        oncam.click_segment(self.TEST_SEG_DATA)
        oncam.click_button(oncam.selectBtn)
        assert (
            oncam.is_segment_display().text == self.TEST_SEG_DATA
        ), "[Fail] 세그먼트 추가 실패"

    @pytest.mark.case_id(16657)
    def test8(self, driver):
        oncam = OnsitePage(driver)

        oncam.click_button(oncam.nextBtn)
        time.sleep(2)
        assert oncam.is_stepper2(), "[Fail] 만들기 2단계 진입 실패"

    @pytest.mark.case_id(16657)
    def test10(self, driver):
        oncam = OnsitePage(driver)

        oncam.click_button(oncam.file_uploadBtn)
        time.sleep(1)

        file_path = BaseClass.getdata_file(self.TEST_IMG)
        oncam.send_file_input(file_path)
        time.sleep(1)
        oncam.click_button(oncam.doneBtn)
        time.sleep(1)
        assert oncam.is_upload_image_display(self.TEST_IMG), "[Fail] 이미지 업로드 실패"

    @pytest.mark.case_id(16657)
    def test11(self, driver):
        oncam = OnsitePage(driver)

        oncam.click_radio_button(oncam.img_link_map)
        oncam.click_button(oncam.clk_area_setting_btn)
        assert oncam.is_click_setting_area_display, "[Fail] 클릭 영역 설정 미노출"

    @pytest.mark.case_id(16657)
    def test12(self, driver):
        oncam = OnsitePage(driver)

        oncam.input_text(oncam.clk_area_setting_name, "테스트")
        oncam.input_url(oncam.clk_area_setting_url, self.TEST_URL)
        oncam.click_button(oncam.save_btn)
        assert oncam.is_preview_display, "[Fail] 클릭 영역 설정 실패"
        time.sleep(1)

    @pytest.mark.case_id(16657)
    def tes13(self, driver):
        oncam = OnsitePage(driver)

        oncam.click_toggle(oncam.title_tgl_off)
        oncam.input_textarea(oncam.title_txt_tf, self.TEST_TITLE_TXT)
        assert oncam.is_title_display().text == self.TEST_TITLE_TXT

    @pytest.mark.case_id(16657)
    def test14(self, driver):
        oncam = OnsitePage(driver)
        camp = CampaignPage(driver)

        oncam.click_toggle(camp.desBtn)
        oncam.input_textarea(camp.input_des, self.TEST_TXT)
        assert oncam.is_blank_display().text == self.TEST_TXT

    @pytest.mark.case_id(16657)
    def test15(self, driver):
        oncam = OnsitePage(driver)
        oncam.click_toggle(oncam.btn_tgl_off)
        oncam.input_text(oncam.btn_txt_tf, self.TEST_BTN_TXT)
        oncam.input_textarea(oncam.btn_url_blank, self.TEST_URL)
        assert oncam.is_btn_display().text == self.TEST_BTN_TXT

    @pytest.mark.case_id(16657)
    def test16(self, driver):
        oncam = OnsitePage(driver)
        camp = CampaignPage(driver)

        oncam.click_button(oncam.nextBtn)
        time.sleep(2)

        oncam.scroll_to_top()
        oncam.click_toggle(oncam.trigger_page_tgl_off)
        oncam.input_chip(oncam.trigger_page_url_tf, self.TEST_URL)
        oncam.input_text(oncam.trigger_page_time_tf, self.TEST_TIME_NUM)
        oncam.input_text(oncam.trigger_page_scroll_tf, self.TEST_PER_NUM)

        oncam.click_listbox(camp.freq_combx)
        oncam.click_listbox(camp.freq_page)
        time.sleep(1)

        oncam.click_button(oncam.saveBtn)
        oncam.click_button(oncam.pause_tab)
        assert oncam.is_camplaign_display(
            self.TEST_TITLE_DATA
        ), "[Fail] 캠페인 생성 실패"
