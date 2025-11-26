import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PageObjects.SegmentPage import SegmentPage
from utilities.BaseClass import BaseClass

class TestSegmentCreate(BaseClass):

    onsite_expect_title = "새로운 세그먼트 만들기 :: GROOBEE"
    onsite1_seg_name = "[QA] 온사이트웹-현재-PC접속 테스트 세그먼트"
    onsite1_seg_des = "온사이트-현재-PC접속"
    onsite2_seg_name = "[QA] 온사이트네이티브-과거x현재-로그인+남자+수요일 테스트 세그먼트"
    onsite2_seg_des = "온사이트네이티브-과거x현재-로그인+남자+수요일"

    def test_segment_create_onsite1(self, driver):
        log = self.get_log()

        groobee = SegmentPage(driver)

        # 세그먼트 타겟팅 메뉴 진입
        groobee.click_segment_menu().click()
        time.sleep(1)

        # 만들기 버튼 클릭
        groobee.click_create_btn().click()
        time.sleep(1)

        # 타이틀 노출까지 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(SegmentPage.seg_title)
        )
        assert driver.title == self.onsite_expect_title

        # 세그먼트명/상세 설명 입력
        groobee.send_seg_name().send_keys(self.onsite1_seg_name)
        groobee.send_seg_des().send_keys(self.onsite1_seg_des)
        time.sleep(1)

        # 타겟 설정
        groobee.click_range_onsite_web().click()
        groobee.click_time_now().click()
        groobee.click_mix_andor().click()
        time.sleep(1)

        # 세그먼트 변수 추가
        groobee.click_add_seg1().click()
        groobee.click_rnb_system().click()
        groobee.click_rnb_system_device().click()
        groobee.click_rnb_choose().click()
        time.sleep(1)

        # 세그먼트 변수 설정
        groobee.click_seg_setting1().click()
        groobee.click_seg_setting1_pc().click()
        groobee.click_seg_setting2().click()
        groobee.click_seg_setting2_yes().click()
        time.sleep(1)

        # 저장(다국어 모달 회피)
        save_btn = groobee.click_save_btn()
        driver.execute_script("arguments[0].click();", save_btn)
        time.sleep(1)

        # 세그먼트 생성 확인
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, f"//p[contains(text(), '{self.onsite1_seg_name}')]")
            )
        )
        assert groobee.get_seg_list_item(self.onsite1_seg_name).is_displayed()
        log.info(f"생성 완료: {self.onsite1_seg_name}")
        time.sleep(1)

    def test_segment_create_onsite2(self, driver):
        log = self.get_log()

        groobee = SegmentPage(driver)

        # 세그먼트 타겟팅 메뉴 진입
        groobee.click_segment_menu().click()
        time.sleep(1)

        # 만들기 버튼 클릭
        groobee.click_create_btn().click()
        time.sleep(1)

        # 타이틀 노출까지 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(SegmentPage.seg_title)
        )
        assert driver.title == self.onsite_expect_title

        # 세그먼트명/상세 설명 입력
        groobee.send_seg_name().send_keys(self.onsite2_seg_name)
        groobee.send_seg_des().send_keys(self.onsite2_seg_des)
        time.sleep(1)

        # 타겟 설정
        groobee.click_range_onsite_native().click()
        groobee.click_time_cross().click()
        time.sleep(1)

        # 세그먼트 변수 추가
        groobee.click_add_seg1().click()
        groobee.click_rnb_visitors().click()
        groobee.click_rnb_visitors_login().click()
        groobee.click_rnb_choose().click()
        time.sleep(1)

        groobee.click_and_btn().click()
        groobee.click_rnb_visitors().click()
        groobee.click_rnb_visitors_gender().click()
        groobee.click_rnb_choose().click()
        time.sleep(1)

        groobee.click_add_seg1().click()
        groobee.click_rnb_visit_rec().click()
        groobee.click_rnb_visit_rec_week().click()
        groobee.click_rnb_choose().click()
        time.sleep(1)

        # 세그먼트 변수 설정
        groobee.click_seg_setting1().click()
        groobee.click_seg_setting1_wed().click()
        groobee.click_seg_setting2().click()
        groobee.click_seg_setting2_yes().click()
        time.sleep(1)

        # 저장(다국어 모달 회피)
        save_btn = groobee.click_save_btn()
        driver.execute_script("arguments[0].click();", save_btn)
        time.sleep(1)

        # 세그먼트 생성 확인
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, f"//p[contains(text(), '{self.onsite2_seg_name}')]")
            )
        )
        assert groobee.get_seg_list_item(self.onsite2_seg_name).is_displayed()
        log.info(f"생성 완료: {self.onsite2_seg_name}")
        time.sleep(1)