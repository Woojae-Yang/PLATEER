import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PageObjects.AisegmentPage import AisegmentPage
from utilities.BaseClass import BaseClass

class TestAisegmentCreate(BaseClass):

    tastes_expect_title = "새로운 취향 분석 세그먼트 만들기 :: GROOBEE"
    main_prod_name = "[QA] 대표 상품 테스트 세그먼트"
    main_prod_des = "대표 상품"
    view_prod_name = "[QA] 많이 조회한 상품 테스트 세그먼트"
    view_prod_des = "많이 조회한 상품"

    def test_aisegment_create_tastes(self, driver):
        log = self.get_log()

        groobee = AisegmentPage(driver)

        # AI 세그먼트 타겟팅 메뉴 진입
        groobee.click_aisegment_menu().click()
        time.sleep(1)

        # 만들기 버튼 클릭
        groobee.click_create_btn().click()
        groobee.click_tastes_seg().click()

        # 타이틀 노출까지 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(AisegmentPage.tastes_seg_title)
        )
        assert driver.title == self.tastes_expect_title

        # 세그먼트명/상세 설명 입력
        groobee.send_tastes_seg_name().send_keys(self.main_prod_name)
        groobee.send_tastes_seg_des().send_keys(self.main_prod_des)

        # 상품 선택
        groobee.click_tastes_handmade().click()
        time.sleep(1)

        # 저장(다국어 모달 회피)
        save_btn = groobee.click_save_btn()
        driver.execute_script("arguments[0].click();", save_btn)

        # 세그먼트 생성 확인
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, f"//p[contains(text(), '{self.main_prod_name}')]")
            )
        )
        assert groobee.get_seg_list_item(self.main_prod_name).is_displayed()
        log.info(f"생성 완료: {self.main_prod_name}")
        time.sleep(1)

        # 만들기 버튼 클릭
        groobee.click_create_btn().click()
        groobee.click_tastes_seg().click()

        # 세그먼트명/상세 설명 입력
        groobee.send_tastes_seg_name().send_keys(self.view_prod_name)
        groobee.send_tastes_seg_des().send_keys(self.view_prod_des)

        # 많이 조회한 상품 전환
        groobee.click_tastes_seg_view().click()
        time.sleep(1)

        # 상품 선택
        groobee.click_tastes_handmade().click()
        time.sleep(1)

        # 저장(다국어 모달 회피)
        save_btn = groobee.click_save_btn()
        driver.execute_script("arguments[0].click();", save_btn)

        # 세그먼트 생성 확인
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, f"//p[contains(text(), '{self.view_prod_name}')]")
            )
        )
        assert groobee.get_seg_list_item(self.view_prod_name).is_displayed()
        log.info(f"생성 완료: {self.view_prod_name}")
        time.sleep(1)