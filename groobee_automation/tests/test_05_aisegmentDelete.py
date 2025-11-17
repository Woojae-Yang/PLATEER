import time
from selenium.webdriver.common.by import By
from PageObjects.AisegmentPage import AisegmentPage
from utilities.BaseClass import BaseClass

class TestAisegmentDelete(BaseClass):

    def test_aisegment_delete(self, driver):
        log = self.get_log()

        groobee = AisegmentPage(driver)

        # AI 세그먼트 타겟팅 메뉴 진입
        groobee.click_aisegment_menu().click()
        time.sleep(1)

        while True:
            # 현재 페이지에서 '테스트 세그먼트' 수집
            segments = driver.find_elements(By.XPATH, "//p[contains(text(),'테스트 세그먼트')]")
            if not segments:
                break

            # 세그먼트 선택
            seg_element = segments[0]
            seg_name = seg_element.text

            # 관리 도구 클릭
            tools_btn = groobee.click_tools_icon_by_name(seg_element, driver)
            tools_btn.click()
            time.sleep(0.2)

            # 삭제 실행
            groobee.click_delete_icon().click()
            time.sleep(0.2)
            groobee.click_delete_icon_confirm().click()
            time.sleep(0.2)

            #삭제 확인
            segments_after = driver.find_elements(By.XPATH, f"//p[contains(text(), '{seg_name}')]")
            assert not segments_after
            log.info(f"삭제 완료: {seg_name}")