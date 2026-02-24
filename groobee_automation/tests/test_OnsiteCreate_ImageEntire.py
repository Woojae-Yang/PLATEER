import pytest
import time
from PageObjects.OnsitePage import OnsitePage
from PageObjects.CampaignPage import CampaignPage
from utilities.BaseClass import BaseClass
from datetime import datetime


@pytest.mark.usefixtures("login")
class TestCreateCampaign(BaseClass):
    today = datetime.now().strftime('%y%m%d')
    
    # 테스트 변수 설정
    TEST_TITLE_DATA = f"[QA][자동화][PC] 이미지전체_{today}"
    TEST_DES_DATA = f"[QA][자동화][PC] 이미지전체_{today}"
    TEST_TAG_DATA = "자동화태그"
    TEST_SEG_DATA = "[QA] 회원 번호"
    TEST_MA_URL = "https://groobee.shop"
    TEST_CA_URL = "https://groobee.shop/product/list.html?cate_no=25"
    TEST_TITLE_TXT = "[QA][자동화]타이틀"
    TEST_TXT = "[QA][Auto]내용"
    TEST_BTN_TXT = "[QA]버튼"
    TEST_IMG = "TestImage.png"

    @pytest.mark.case_id(17178)
    def test_17178(self, driver, clear_campaigns):
        
        oncam = OnsitePage(driver)

        oncam.click_menu(oncam.campaignMenu)
        clear_campaigns(oncam)

        oncam.click_tab(oncam.pause_tab)
        oncam.move_storage(driver)
        
        oncam.click_tab(oncam.storage_tab)
        oncam.delete_campaign(driver)

        oncam.click_button(oncam.createBtn)
        oncam.click_dropdown(oncam.create_dropdown_onsite)
        assert oncam.is_stepper1(), "[Fail] 만들기 1단계 진입 실패"

    @pytest.mark.case_id(17179)
    def test_17179(self, driver):
        oncam = OnsitePage(driver)

        oncam.input_text(oncam.campaign_name_input, self.TEST_TITLE_DATA)
        result = (oncam.is_campaign_reg_name().get_attribute("value") == self.TEST_TITLE_DATA)
        assert result, "[Fail] 캠페인명 입력 실패"

    @pytest.mark.case_id(17180)
    def test_17180(self, driver):
        oncam = OnsitePage(driver)

        oncam.input_text(oncam.campaign_des_input, self.TEST_DES_DATA)
        result = (oncam.is_campaign_reg_des().get_attribute("value") == self.TEST_DES_DATA)
        assert result, "[Fail] 상세설명 입력 실패"

    @pytest.mark.case_id(17181)
    def test_17181(self, driver):
        oncam = OnsitePage(driver)

        oncam.click_button(oncam.tag_btn)
        assert oncam.is_add_tag_modal(), "[Fail] 모달 미노출"

    @pytest.mark.case_id(17182)
    def test_17182(self, driver):
        oncam = OnsitePage(driver)

        oncam.input_chip(oncam.com_tag_input, self.TEST_TAG_DATA)
        oncam.click_button(oncam.com_tag_add_btn)
        time.sleep(1)
        result = oncam.is_added_tag(self.TEST_TAG_DATA)
        assert result, "[Fail] 태그 추가 실패"

    @pytest.mark.case_id(17183)
    def test_17183(self, driver):
        oncam = OnsitePage(driver)
        result = oncam.click_access_type(oncam.access_type_pc)
        assert result, "[Fail] 접속 유형 선택 실패"

    @pytest.mark.case_id(17184)
    def test_17184(self, driver):
        oncam = OnsitePage(driver)

        oncam.click_button(oncam.seg_load)
        oncam.click_tab(oncam.seg_tab)
        oncam.click_segment(self.TEST_SEG_DATA)
        oncam.click_button(oncam.selectBtn)
        assert (oncam.is_segment_display().text == self.TEST_SEG_DATA), "[Fail] 세그먼트 추가 실패"

    @pytest.mark.case_id(17185)
    def test_17185(self, driver):
        oncam = OnsitePage(driver)

        oncam.click_button(oncam.nextBtn)
        time.sleep(2)
        assert oncam.is_stepper2(), "[Fail] 만들기 2단계 진입 실패"

    @pytest.mark.case_id(17186)
    def test_17186(self, driver):
        oncam = OnsitePage(driver)

        oncam.click_button(oncam.file_uploadBtn)
        time.sleep(1)

        file_path = BaseClass.getdata_file(self.TEST_IMG)
        oncam.send_file_input(file_path)
        time.sleep(1)
        oncam.click_button(oncam.doneBtn)
        time.sleep(1)
        assert oncam.is_upload_image_display(self.TEST_IMG), "[Fail] 이미지 업로드 실패"


    @pytest.mark.case_id(17187)
    def test_17187(self, driver):
        oncam = OnsitePage(driver)

        oncam.click_radio_button(oncam.img_link_entire)
        oncam.input_textarea(oncam.clk_area_setting_url, self.TEST_CA_URL)
        assert oncam.get_text(oncam.clk_area_setting_url) == self.TEST_CA_URL, "[Fail] 이미지 전체 설정 실패"


    @pytest.mark.case_id(17188)
    def test_17188(self, driver):
        oncam = OnsitePage(driver)

        oncam.click_toggle(oncam.title_tgl_off)
        oncam.input_textarea(oncam.title_txt_tf, self.TEST_TITLE_TXT)
        assert oncam.get_text(oncam.title_txt_tf) == self.TEST_TITLE_TXT, "[Fail] 타이틀 입력 실패"

    @pytest.mark.case_id(17189)
    def test_17189(self, driver):
        oncam = OnsitePage(driver)
        camp = CampaignPage(driver)

        oncam.click_toggle(camp.desBtn)
        oncam.input_textarea(camp.input_des, self.TEST_TXT)
        assert oncam.get_text(camp.input_des) == self.TEST_TXT, "[Fail] 내용 입력 실패"

    @pytest.mark.case_id(17191)
    def test_17191(self, driver):
        oncam = OnsitePage(driver)
        oncam.click_toggle(oncam.btn_tgl_off)
        oncam.input_text(oncam.btn_txt_tf, self.TEST_BTN_TXT)
        oncam.input_textarea(oncam.btn_url_blank, self.TEST_MA_URL)
        assert oncam.get_text(oncam.btn_url_blank) == self.TEST_MA_URL, "[Fail] 버튼 입력 실패"

    @pytest.mark.case_id(17192)
    def test_17192(self, driver):
        oncam = OnsitePage(driver)

        oncam.click_button(oncam.nextBtn)
        time.sleep(1)
        assert oncam.is_stepper3(), "[Fail] 만들기 3단계 진입 실패"

    @pytest.mark.case_id(17193)
    def test_17193(self, driver):
        oncam = OnsitePage(driver)
        camp = CampaignPage(driver)

        oncam.click_listbox(camp.freq_combx)
        oncam.click_listbox(camp.freq_page)

        oncam.click_button(oncam.saveBtn)
        time.sleep(1)

        assert driver.title == oncam.list_title, "[Fail] 캠페인 생성 실패"

    @pytest.mark.case_id(17194)
    def test_17194(self, driver):
        oncam = OnsitePage(driver)
        
        oncam.click_button(oncam.pause_tab)

        assert oncam.is_camplaign_display(self.TEST_TITLE_DATA), "[Fail] 중지 상태의 캠페인 미노출"
        
    @pytest.mark.case_id(17195)
    def test_17195(self, driver):
        oncam = OnsitePage(driver)
        oncam.click_button(oncam.status_icon_pause)
        time.sleep(1)

        oncam.click_button(oncam.status_icon_confirm)
        oncam.click_tab(oncam.progress_tab)
        time.sleep(1)
        assert oncam.is_camplaign_display(self.TEST_TITLE_DATA), "[Fail] 진행 상태의 캠페인 미노출"

    @pytest.mark.case_id(17196)
    def test_17196(self, driver):
        oncam = OnsitePage(driver)
        camp = CampaignPage(driver)

        oncam.open_new_tab(self.TEST_MA_URL)
        
        time.sleep(1)
        oncam.click_button(oncam.test_login)
        time.sleep(1)
        oncam.input_text(oncam.test_id_tf, "jekim26021201")
        oncam.input_text(oncam.test_pw_tf, "admin0218?")
        oncam.click_button(oncam.test_login_btn)

        time.sleep(1)
        assert oncam.is_campaign_display(camp.cam_popup), "[Fail] 캠페인 미노출"

    @pytest.mark.case_id(17197)
    def test_17197(self, driver):
        oncam = OnsitePage(driver)

        time.sleep(1)
        oncam.click_image(oncam.camp_img)
        time.sleep(1)
        assert oncam.get_current_url() == self.TEST_CA_URL, "[Fail] 캠페인 클릭 실패"

    @pytest.mark.case_id(17207)
    def test_17207(self, driver):
        oncam = OnsitePage(driver)

        oncam.click_image(oncam.test_product)
        oncam.click_button(oncam.test_buy_btn)
        oncam.input_text(oncam.test_or_name, "test")
        oncam.click_listbox(oncam.test_or_bank_list)
        oncam.click_listbox(oncam.test_or_bank_list1)
        oncam.click_checkbox(oncam.test_or_agree_btn)
        oncam.click_listbox(oncam.test_or_buy_btn)
        time.sleep(1)
        
        result = BaseClass.wait_visible(driver, oncam.test_or_comp)
        assert result, "[Fail] 주문 실패"

    @pytest.mark.case_id(17198)
    def test_17198(self, driver):
        oncam = OnsitePage(driver)

        oncam.switch_tab(oncam.list_title)
        driver.refresh()
        time.sleep(1)
        oncam.click_button(oncam.more_btn)
        oncam.click_listbox(oncam.report_icon)
        
        time.sleep(2)
        assert driver.title == oncam.report_title, "[Fail] 분석 리포트 진입 실패"
        
    @pytest.mark.case_id(17199)
    def test_17199(self, driver):
        oncam = OnsitePage(driver)
        assert oncam.get_textContent(oncam.exp_cnt) == "1 건", "[Fail] 노출 수 이상"
    
    @pytest.mark.case_id(17200)
    def test_17200(self, driver):
        oncam = OnsitePage(driver)
        assert oncam.get_textContent(oncam.clk_cnt) == "1 건", "[Fail] 클릭 수 이상"

        oncam.click_button(oncam.clk_detail)
        assert oncam.get_textContent(oncam.clk_datail_img_a) == "1", "[Fail] 클릭 수 상세 이상"

    @pytest.mark.case_id(17202)
    def test_17202(self, driver):
        oncam = OnsitePage(driver)
        assert oncam.get_textContent(oncam.or_cnt_tot) == "1 건", "[Fail] 주문 수(전체) 이상"
        assert oncam.get_textContent(oncam.or_cnt_clk) == "1 건", "[Fail] 주문 수(클릭) 이상"

    @pytest.mark.case_id(17203)
    def test_17203(self, driver):
        oncam = OnsitePage(driver)
        assert oncam.get_textContent(oncam.conv_amt_cnt_tot) == "261,360 원", "[Fail] 전환 금액(전체) 이상"
        assert oncam.get_textContent(oncam.conv_amt_cnt_clk) == "261,360 원", "[Fail] 전환 금액(클릭) 이상"
    
    @pytest.mark.case_id(17204)
    def test_17204(self, driver):
        oncam = OnsitePage(driver)
        assert oncam.get_textContent(oncam.clk_conv_per) == "100%", "[Fail] 클릭 전환율 이상"

    @pytest.mark.case_id(17205)
    def test_17205(self, driver):
        oncam = OnsitePage(driver)
        assert oncam.get_textContent(oncam.signup_conv_tot) == "0%", "[Fail] 회원가입 전환율(전체) 이상"
        assert oncam.get_textContent(oncam.signup_conv_clk) == "0%", "[Fail] 회원가입 전환율(클릭) 이상"

    @pytest.mark.case_id(17206)
    def test_17206(self, driver):        
        oncam = OnsitePage(driver)
        assert oncam.get_textContent(oncam.or_conv_tot) == "100%", "[Fail] 주문 전환율(전체) 수 이상"
        assert oncam.get_textContent(oncam.or_conv_clk) == "100%", "[Fail] 주문 전환율(클릭) 이상"


        




        