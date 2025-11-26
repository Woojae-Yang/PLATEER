import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PageObjects.AisegmentPage import AisegmentPage
from utilities.BaseClass import BaseClass

class TestAisegmentCreate(BaseClass):

    rfm_expect_title = "새로운 RFM 세그먼트 만들기 :: GROOBEE"

    def test_aisegment_create_rfm(self, driver):
        log = self.get_log()

        groobee = AisegmentPage(driver)

        # AI 세그먼트 타겟팅 메뉴 진입
        groobee.click_aisegment_menu().click()
        time.sleep(1)

        # 만들기 버튼 클릭
        groobee.click_create_btn().click()
        groobee.click_rfm_seg().click()

        # 타이틀 노출까지 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(AisegmentPage.rfm_seg_title)
        )
        assert driver.title == self.rfm_expect_title

        # dict로 RFM 세그먼트 옵션 불러오기
        rfm_options = groobee.get_rfm_options()

        for i, rfm_name in enumerate(rfm_options.keys()):
            # 세그먼트명/상세 설명 입력
            seg_name_text = f"[QA] {rfm_name} 테스트 세그먼트"
            seg_des_text = f"{rfm_name}"
            groobee.send_rfm_seg_name().send_keys(seg_name_text)
            groobee.send_rfm_seg_des().send_keys(seg_des_text)

            # RFM 세그먼트 선택
            rfm_element = driver.find_element(By.XPATH, f"//h6[contains(text(), '{rfm_name}')]")
            rfm_element.click()
            time.sleep(1)

            # 저장(다국어 모달 회피)
            save_btn = groobee.click_save_btn()
            driver.execute_script("arguments[0].click();", save_btn)

            # 세그먼트 생성 확인
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH, f"//p[contains(text(), '{seg_name_text}')]")
                )
            )
            assert groobee.get_seg_list_item(seg_name_text).is_displayed()
            log.info(f"생성 완료: {seg_name_text}")
            time.sleep(1)

            # 마지막 루프 제외
            if i != len(rfm_options) - 1:
                groobee.click_create_btn().click()
                groobee.click_rfm_seg().click()
                # 타이틀 노출까지 대기
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(AisegmentPage.rfm_seg_title)
                )
                assert driver.title == self.rfm_expect_title