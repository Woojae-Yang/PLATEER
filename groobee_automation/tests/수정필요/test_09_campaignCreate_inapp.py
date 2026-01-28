import time
import os
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PageObjects.수정필요.CampaignPage import CampaignPage
from utilities.BaseClass import BaseClass

class TestCampaignCreate(BaseClass):

    campaign_expect_title = "새로운 인앱 메시지 캠페인 만들기 :: GROOBEE"
    campaign_name = "[QA] 반복-방문페이지마다 테스트 캠페인"
    campaign_des = "반복-방문페이지마다"
    campaign_url = "https://groobee.shop/product/list.html?cate_no=24"
    campaign_link = "myapp://123"
    campaign_txt = "신상품으로 이동하기"

    def test_campaign_create_inapp(self, driver):
        log = self.get_log()

        groobee = CampaignPage(driver)

        # 온사이트 캠페인 메뉴 진입
        groobee.click_campaign_menu().click()
        time.sleep(1)

        # 만들기 버튼 클릭
        groobee.click_create_btn().click()
        time.sleep(1)

        # 인앱 메시지 캠페인 선택
        groobee.click_create_btn_inapp().click()
        time.sleep(1)

        # 타이틀 노출까지 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(CampaignPage.cam_title)
        )
        assert driver.title == self.campaign_expect_title, f"현재 페이지: {driver.title}, 기대 페이지: {self.campaign_expect_title}"

        # 캠페인명/상세 설명 입력
        groobee.send_cam_name().send_keys(self.campaign_name)
        groobee.send_cam_des().send_keys(self.campaign_des)
        time.sleep(1)

        # 타겟 설정
        groobee.click_seg_load().click()
        time.sleep(1)

        # 세그먼트 불러오기 RNB
        groobee.click_seg_tab().click()
        time.sleep(1)

        seg_list = groobee.click_now_os_seg()
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

        # 다음 단계(다국어 모달 회피)
        next_btn = groobee.click_next_btn()
        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(1)

        # A안 디자인
        groobee.click_a_type().click()
        time.sleep(1)
        groobee.click_design_popup().click()
        time.sleep(1)

        # 파일 업로드 RNB
        groobee.click_file_upload_btn().click()
        time.sleep(1)

        # 업로드할 파일 경로 찾기
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, ".."))
        testdata_path = os.path.join(project_root, "TestData")
        file_path = os.path.join(testdata_path, "JPEGTest1080.jpg")
        groobee.send_file_input().send_keys(file_path)
        time.sleep(1)

        # 파일 업로드 RNB 닫기
        groobee.click_done_btn().click()
        time.sleep(1)

        # URL 입력
        groobee.send_input_url().send_keys(self.campaign_url)
        time.sleep(1)

        # 스타일
        groobee.click_corner_style().click()
        time.sleep(1)

        # B안 디자인
        groobee.click_add_btn().click()
        time.sleep(1)
        groobee.click_b_type().click()
        time.sleep(1)
        groobee.click_design_sticky_default().click()
        time.sleep(1)

        # 내용 입력
        groobee.send_input_txt20().send_keys(self.campaign_txt)
        time.sleep(1)
        groobee.click_bold_cbx().click()
        groobee.click_sort_mid().click()
        time.sleep(1)
        groobee.send_input_url().send_keys(self.campaign_url)
        time.sleep(1)

        # 스타일
        groobee.click_corner_style().click()
        time.sleep(1)

        # 노출 위치
        groobee.click_set_bottom().click()
        time.sleep(1)

        # C안 디자인
        groobee.click_add_btn().click()
        time.sleep(1)
        groobee.click_c_type().click()
        time.sleep(1)
        groobee.click_design_sticky_btn().click()
        time.sleep(1)

        # 파일 업로드 RNB
        groobee.click_file_upload_btn().click()
        time.sleep(1)

        # 업로드할 파일 경로 찾기
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, ".."))
        testdata_path = os.path.join(project_root, "TestData")
        file_path = os.path.join(testdata_path, "PNGTest360.jpg")
        groobee.send_file_input().send_keys(file_path)
        time.sleep(1)

        # 파일 업로드 RNB 닫기
        groobee.click_done_btn().click()
        time.sleep(1)

        # 타이틀
        groobee.send_input_txt16().send_keys(self.campaign_txt)
        time.sleep(1)
        groobee.click_bold_cbx().click()
        time.sleep(1)

        # 내용
        groobee.send_input_txt40().send_keys(self.campaign_des)
        time.sleep(1)
        groobee.click_bold_cbx2().click()
        time.sleep(1)

        # 버튼
        groobee.send_input_txt15().send_keys(self.campaign_txt)
        time.sleep(1)
        groobee.click_bold_cbx3().click()
        time.sleep(1)
        groobee.send_input_url().send_keys(self.campaign_url)
        time.sleep(1)

        # 스타일
        groobee.click_corner_style().click()
        time.sleep(1)

        # 노출 위치
        groobee.click_set_top().click()
        time.sleep(1)

        # A/B/N 테스트 설정
        groobee.click_type_auto().click()
        time.sleep(1)
        groobee.click_target_order().click()
        time.sleep(1)

        # 다음 단계(다국어 모달 회피)
        next_btn = groobee.click_next_btn()
        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(1)

        # 스케줄
        groobee.click_period_set().click()
        time.sleep(1)
        groobee.click_repeat_true().click()
        time.sleep(1)
        groobee.click_repeat_setting().click()
        time.sleep(1)
        groobee.click_repeat_setting_done().click()
        time.sleep(1)

        # 노출 빈도
        groobee.click_freq_combx().click()
        time.sleep(1)
        groobee.click_freq_page().click()
        time.sleep(1)

        # 저장(다국어 모달 회피)
        save_btn = groobee.click_save_btn()
        driver.execute_script("arguments[0].click();", save_btn)
        time.sleep(1)

        # 캠페인 생성 확인
        groobee.click_pause_tab().click()
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, f"//p[contains(text(), '{self.campaign_name}')]")
            )
        )
        assert groobee.get_cam_list_item(self.campaign_name).is_displayed(), f"생성 실패: {self.campaign_name}"
        log.info(f"생성 완료: {self.campaign_name}")
        time.sleep(1)

        # 상태 변경
        groobee.click_status_icon_pause().click()
        time.sleep(1)
        groobee.click_status_icon_confirm().click()
        time.sleep(1)
        groobee.click_progress_tab().click()
        time.sleep(1)