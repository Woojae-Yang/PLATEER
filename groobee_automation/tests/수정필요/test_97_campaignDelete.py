import time
from selenium.webdriver.common.by import By
from PageObjects.수정필요.CampaignPage import CampaignPage
from utilities.BaseClass import BaseClass

class TestCampaignDelete(BaseClass):

    def test_campaign_delete(self, driver):
        log = self.get_log()

        groobee = CampaignPage(driver)

        # 온사이트 캠페인 메뉴 진입
        groobee.click_campaign_menu().click()
        time.sleep(1)

        while True:
            # 현재 페이지에서 '테스트 캠페인' 수집
            segments = driver.find_elements(By.XPATH, "//p[contains(text(),'테스트 캠페인')]")
            if not segments:
                break

            seg_element = segments[0]
            seg_name = seg_element.text

            # 상태 변경 전 seg_element 새로 조인
            seg_element = driver.find_element(By.XPATH, f"//p[contains(text(), '{seg_name}')]")

            # 상태 변경
            status_btn = groobee.click_status_icon_by_name(seg_element, driver)
            status_btn.click()
            time.sleep(0.5)
            groobee.click_status_icon_confirm().click()
            time.sleep(0.5)

            # 중지중 탭 이동
            groobee.click_pause_tab().click()
            time.sleep(0.5)

            # 중지중 탭에서도 다시 seg_element 재획득
            seg_element = driver.find_element(By.XPATH, f"//p[contains(text(), '{seg_name}')]")

            # 관리 도구 클릭
            tools_btn = groobee.click_tools_icon_by_name(seg_element, driver)
            tools_btn.click()
            time.sleep(0.5)

            # 보관함으로 이동
            groobee.click_moveto_storage_icon().click()
            time.sleep(0.5)

            # 보관함 탭 이동
            groobee.click_storage_tab().click()
            time.sleep(0.5)

            # 보관함에서도 seg_element 재획득
            seg_element = driver.find_element(By.XPATH, f"//p[contains(text(), '{seg_name}')]")

            # 관리 도구 클릭
            tools_btn = groobee.click_tools_icon_by_name(seg_element, driver)
            tools_btn.click()
            time.sleep(0.5)

            # 삭제 실행
            groobee.click_delete_icon().click()
            time.sleep(0.5)
            groobee.click_delete_icon_confirm().click()
            time.sleep(0.5)

            # 보관함 탭 이동
            groobee.click_progress_tab().click()
            time.sleep(0.5)

            # 삭제 확인
            segments_after = driver.find_elements(By.XPATH, f"//div[contains(text(), '{seg_name}')]")
            assert not segments_after, f"삭제 실패: {seg_name}"
            log.info(f"삭제 완료: {seg_name}")