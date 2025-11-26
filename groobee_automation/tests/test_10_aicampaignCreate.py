import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PageObjects.RecommendPage import RecommendPage
from utilities.BaseClass import BaseClass

class TestAiCampaignCreate(BaseClass):

    aicampaign_expect_title = "새로운 AI 상품 추천 캠페인 만들기 :: GROOBEE"
    aicampaign_name = "[QA] 상품 추천-구매 확률-데이터 호출형 테스트 캠페인"
    aicampaign_des = "상품 추천-구매 확률-데이터 호출형"

    def test_aicampaign_create(self, driver):
        log = self.get_log()

        groobee = RecommendPage(driver)

        # AI 상품 추천 캠페인 메뉴 진입
        groobee.click_recommend_menu().click()
        time.sleep(1)

        # 만들기 버튼 클릭
        groobee.click_create_btn().click()

        # 타이틀 노출까지 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(RecommendPage.cam_title)
        )
        assert driver.title == self.aicampaign_expect_title

        # 캠페인명/상세 설명 입력
        groobee.send_cam_name().send_keys(self.aicampaign_name)
        groobee.send_cam_des().send_keys(self.aicampaign_des)
        time.sleep(1)

        # 접속 유형 설정
        groobee.click_type_pcweb().click()

        # 알고리즘 설정(다국어 모달 회피)
        groobee.click_set_algo_goods().click()
        goods_all_cb = groobee.click_goods_all_cb()
        driver.execute_script("arguments[0].click();", goods_all_cb)
        visitors_all_cb = groobee.click_visitors_all_cb()
        driver.execute_script("arguments[0].click();", visitors_all_cb)
        stat_all_cb = groobee.click_stat_all_cb()
        driver.execute_script("arguments[0].click();", stat_all_cb)
        time.sleep(1)

        # 타겟 설정
        groobee.click_target_set().click()
        groobee.click_seg_load().click()
        time.sleep(1)

        # 세그먼트 불러오기 RNB
        groobee.click_aiseg_tab().click()
        groobee.click_purchase_self_seg().click()
        groobee.click_select_btn().click()
        time.sleep(1)

        # 다음 단계(다국어 모달 회피)
        next_btn = groobee.click_next_btn()
        driver.execute_script("arguments[0].click();", next_btn)

        # 디자인 유형
        groobee.click_design_script().click()
        time.sleep(0.5)

        # 다음 단계(다국어 모달 회피)
        next_btn = groobee.click_next_btn()
        driver.execute_script("arguments[0].click();", next_btn)

        # 필터링 설정
        groobee.click_filter_order().click()
        time.sleep(0.5)

        # 스케줄
        groobee.click_schedule_self().click()
        time.sleep(0.5)

        # 저장(다국어 모달 회피)
        save_btn = groobee.click_save_btn()
        driver.execute_script("arguments[0].click();", save_btn)

        # 세그먼트 생성 확인
        groobee.click_pause_tab().click()
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, f"//p[contains(text(), '{self.aicampaign_name}')]")
            )
        )
        assert groobee.get_cam_list_item(self.aicampaign_name).is_displayed()
        log.info(f"생성 완료: {self.aicampaign_name}")
        time.sleep(1)

        # 상태 변경
        groobee.click_status_icon_pause().click()
        time.sleep(1)
        groobee.click_status_icon_confirm().click()
        time.sleep(1)
        groobee.click_progress_tab().click()
        time.sleep(1)