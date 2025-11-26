import time
import os
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PageObjects.CampaignPage import CampaignPage
from utilities.BaseClass import BaseClass

class TestCampaignCreate(BaseClass):

    campaign_expect_title = "새로운 온사이트 캠페인 만들기 :: GROOBEE"
    service_expect_title = "기본 레이아웃"
    campaign_name = "[QA] PC/웹-페이지반복 테스트 캠페인"
    campaign_des = "PC/웹-페이지반복"
    campaign_url = "https://groobee.shop/product/list.html?cate_no=24"
    campaign_txt = "신상품으로 이동하기"

    def test_campaign_create(self, driver):
        log = self.get_log()

        groobee = CampaignPage(driver)

        # AI 상품 추천 캠페인 메뉴 진입
        groobee.click_campaign_menu().click()
        time.sleep(1)

        # 만들기 버튼 클릭
        groobee.click_create_btn().click()

        # 타이틀 노출까지 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(CampaignPage.cam_title)
        )
        assert driver.title == self.campaign_expect_title

        # 캠페인명/상세 설명 입력
        groobee.send_cam_name().send_keys(self.campaign_name)
        groobee.send_cam_des().send_keys(self.campaign_des)
        time.sleep(1)

        # 접속 유형 설정
        groobee.click_type_pcweb().click()
        time.sleep(0.5)

        # 타겟 설정
        groobee.click_seg_load().click()
        time.sleep(0.5)

        # 세그먼트 불러오기 RNB
        groobee.click_seg_tab().click()
        time.sleep(0.5)
        groobee.click_now_pc_seg().click()
        time.sleep(0.5)
        groobee.click_select_btn().click()
        time.sleep(1)

        # 다음 단계(다국어 모달 회피)
        next_btn = groobee.click_next_btn()
        driver.execute_script("arguments[0].click();", next_btn)

        # 파일 업로드 RNB
        groobee.click_file_upload_btn().click()
        time.sleep(1)

        # 업로드할 파일 경로 찾기
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, ".."))
        testdata_path = os.path.join(project_root, "TestData")
        file_path = os.path.join(testdata_path, "TestImage.jpg")
        groobee.send_file_input().send_keys(file_path)
        time.sleep(1)

        # 파일 업로드 RNB 닫기
        groobee.click_done_btn().click()
        time.sleep(1)

        # URL 입력
        groobee.send_input_url().send_keys(self.campaign_url)
        time.sleep(0.5)

        # 내용 입력
        groobee.click_des_btn().click()
        groobee.send_input_des().send_keys(self.campaign_txt)
        time.sleep(0.5)

        # 노출 위치 설정
        groobee.click_set_br().click()
        time.sleep(0.5)

        # 다음 단계(다국어 모달 회피)
        next_btn = groobee.click_next_btn()
        driver.execute_script("arguments[0].click();", next_btn)

        # 노출 빈도
        groobee.click_freq_combx().click()
        groobee.click_freq_page().click()
        groobee.click_priority_cb().click()
        time.sleep(1)

        # 저장(다국어 모달 회피)
        save_btn = groobee.click_save_btn()
        driver.execute_script("arguments[0].click();", save_btn)

        # 세그먼트 생성 확인
        groobee.click_pause_tab().click()
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, f"//p[contains(text(), '{self.campaign_name}')]")
            )
        )
        assert groobee.get_cam_list_item(self.campaign_name).is_displayed()
        log.info(f"생성 완료: {self.campaign_name}")
        time.sleep(1)

        # 상태 변경
        groobee.click_status_icon_pause().click()
        time.sleep(1)
        groobee.click_status_icon_confirm().click()
        time.sleep(1)
        groobee.click_progress_tab().click()
        time.sleep(1)

    def test_campaign_service(self, driver):
        log = self.get_log()

        groobee = CampaignPage(driver)

        # 윈도우 핸들
        main_window = driver.current_window_handle
        new_window = None

        # 몰 바로가기
        groobee.click_admin_icon().click()
        groobee.click_goto_mall().click()

        # 새 창 찾기
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
        all_windows = driver.window_handles
        for handle in all_windows:
            if handle != main_window:
                new_window = handle
                break

        # 새 창 윈도우 전환
        driver.switch_to.window(new_window)
        time.sleep(2)

        # 캠페인 노출 확인
        groobee.click_cam_popup().click()
        time.sleep(2)
        assert driver.title == self.service_expect_title
        log.info(f"캠페인 클릭: {self.service_expect_title}")

        # 기존 창 윈도우 전환
        driver.close()
        driver.switch_to.window(main_window)
        time.sleep(1)