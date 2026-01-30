from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
from utilities.BaseClass import BaseClass

class GroobeeActions:

    def __init__(self, driver):
        self.driver = driver

    # -------------------------element 선언 영역-------------------------
    # LNB
    dashboardMenu = (By.XPATH, "//p[contains(text(),'대시보드')]")
    monitoringMenu = (By.XPATH, "//p[contains(text(),'실시간')]")
    datamonitoringMenu = (By.XPATH, "//p[contains(text(),'데이터 모니터링')]")
    aisegmentMenu = (By.XPATH, "//a[@href='/aisegment']")
    segmentMenu = (By.XPATH, "//a[@href='/segment']")
    recommendMenu = (By.XPATH, "//p[contains(text(),'AI 상품 추천 캠페인')]")
    campaignMenu = (By.XPATH, "//p[contains(text(),'온사이트 캠페인')]")
    pushnotiMenu = (By.XPATH, "//p[contains(text(),'푸시 알림 캠페인')]")
    kakaobrandMenu = (By.XPATH, "//p[contains(text(),'카카오톡 캠페인: 브랜드 메시지')]")
    kakaomomentMenu = (By.XPATH, "//p[contains(text(),'카카오톡 캠페인: 모먼트')]")
    kakaoalimMenu = (By.XPATH, "//p[contains(text(),'카카오톡 캠페인: 알림톡')]")
    settingMenu = (By.XPATH, "//p[contains(text(),'설정')]")

    # 상태탭
    progress_tab = (By.XPATH, "//button[contains(text(),'진행중')]")
    pause_tab = (By.XPATH, "//button[contains(text(),'중지중')]")
    storage_tab = (By.XPATH, "//button[contains(text(),'보관함')]")

    # 상태 아이콘
    status_icon_play = (By.XPATH, "//div[@class='MuiDataGrid-row']//button[.//*[name()='svg' and @data-testid='PlayArrowIcon']]")
    status_icon_pause = (By.XPATH, "//div[@class='MuiDataGrid-row']//button[.//*[name()='svg' and @data-testid='PauseOutlinedIcon']]")
    status_icon_cancel = (By.XPATH, "//button[contains(text(),'취소')]")
    status_icon_confirm = (By.XPATH, "//button[contains(text(),'확인')]")

    # 관리 도구
    tools_icon = (By.XPATH, "//div[@class='MuiDataGrid-row']//button[.//*[name()='svg' and @data-testid='MoreHorizIcon']]")
    update_icon = (By.XPATH, "//p[contains(text(),'수정')]")
    copy_icon = (By.XPATH, "//p[contains(text(),'복사')]")
    report_icon = (By.XPATH, "//p[contains(text(),'분석 리포트')]")
    view_icon = (By.XPATH, "//p[contains(text(),'미리보기')]")
    exclusion_icon = (By.XPATH, "//p[contains(text(),'제외 조건 설정')]")
    code_copy_icon = (By.XPATH, "//p[contains(text(),'코드 복사')]")
    moveto_storage = (By.XPATH, "//p[contains(text(),'보관함으로 이동')]")
    moveto_pause = (By.XPATH, "//p[contains(text(),'중지중으로 이동')]")
    delete_icon = (By.XPATH, "//p[contains(text(),'삭제')]")
    delete_icon_cancel = (By.XPATH, "//button[contains(text(),'취소')]")
    delete_icon_confirm = (By.XPATH, "//button[contains(text(),'확인')]")

    # 캠페인 리스트 읽기
    grid_rows = (By.XPATH, "//div[contains(@class,'MuiDataGrid-row') and @data-rowindex]")

    # -------------------------동작 선언 영역-------------------------
    # LNB
    def click_dashboard_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.dashboardMenu, timeout).click()
    def click_monitoring_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.monitoringMenu, timeout).click()
    def click_datamonitoring_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.datamonitoringMenu, timeout).click()
    def click_aisegment_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.aisegmentMenu, timeout).click()
    def click_segment_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.segmentMenu, timeout).click()
    def click_recommend_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.recommendMenu, timeout).click()
    def click_campaign_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.campaignMenu, timeout).click()
    def click_pushnoti_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.pushnotiMenu, timeout).click()
    def click_kakaobrand_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.kakaobrandMenu, timeout).click()
    def click_kakaomoment_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.kakaomomentMenu, timeout).click()
    def click_kakaoalim_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.kakaoalimMenu, timeout).click()
    def click_setting_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.settingMenu, timeout).click()

    # 상태탭
    def click_progress_tab(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.progress_tab, timeout).click()
    def click_pause_tab(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.pause_tab, timeout).click()
    def click_storage_tab(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.storage_tab, timeout).click()

    # 상태 아이콘
    def click_status_icon_play(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.status_icon_play, timeout).click()
    def click_status_icon_pause(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.status_icon_pause, timeout).click()
    def click_status_icon_cancel(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.status_icon_cancel, timeout).click()
    def click_status_icon_confirm(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.status_icon_confirm, timeout).click()

    # 관리 도구
    def click_tools_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.tools_icon, timeout).click()
    def click_update_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.update_icon, timeout).click()
    def click_copy_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.copy_icon, timeout).click()
    def click_report_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.report_icon, timeout).click()
    def click_view_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.view_icon, timeout).click()
    def click_exclusion_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.exclusion_icon, timeout).click()
    def click_code_copy_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.code_copy_icon, timeout).click()
    def click_moveto_storage_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.moveto_storage, timeout).click()
    def click_moveto_pause_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.moveto_pause, timeout).click()
    def click_delete_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.delete_icon, timeout).click()
    def click_delete_icon_cancel(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.delete_icon_cancel, timeout).click()
    def click_delete_icon_confirm(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.delete_icon_confirm, timeout).click()

    # 관리 도구(…) 아이콘 찾기
    @staticmethod
    def click_tools_icon_by_name(cam_element, driver):
        row = cam_element.find_element(
            By.XPATH, "./ancestor-or-self::div[contains(@class,'MuiDataGrid-row')]"
        )
        row_index = row.get_attribute("data-rowindex")

        pinned_container = driver.find_element(
            By.XPATH, "//div[contains(@class,'MuiDataGrid-pinnedColumns--right')]"
        )
        buttons = pinned_container.find_elements(
            By.XPATH, ".//button[contains(@class,'MuiIconButton-root')]"
        )

        for btn in buttons:
            btn_row = btn.find_element(
                By.XPATH, "./ancestor-or-self::div[contains(@class,'MuiDataGrid-row')]"
            )
            if btn_row.get_attribute("data-rowindex") == row_index:
                return btn

        raise NoSuchElementException(f"{row_index} 행에서 tools 아이콘을 찾을 수 없음")

    # 상태 아이콘(재생/일시정지) 찾기
    @staticmethod
    def click_status_icon_by_name(cam_element, driver):
        row = cam_element.find_element(
            By.XPATH, "./ancestor-or-self::div[contains(@class,'MuiDataGrid-row')]"
        )
        row_index = row.get_attribute("data-rowindex")

        # 1) row 내부
        try:
            return row.find_element(
                By.XPATH,
                ".//button[.//*[name()='svg' and "
                "(@data-testid='PlayArrowIcon' or @data-testid='PauseOutlinedIcon')]]"
            )
        except NoSuchElementException:
            pass

        # 2) pinned fallback
        pinned_container = driver.find_element(
            By.XPATH, "//div[contains(@class,'MuiDataGrid-pinnedColumns--right')]"
        )
        status_buttons = pinned_container.find_elements(
            By.XPATH,
            ".//button[.//*[name()='svg' and "
            "(@data-testid='PlayArrowIcon' or @data-testid='PauseOutlinedIcon')]]"
        )

        for btn in status_buttons:
            btn_row = btn.find_element(
                By.XPATH, "./ancestor-or-self::div[contains(@class,'MuiDataGrid-row')]"
            )
            if btn_row.get_attribute("data-rowindex") == row_index:
                return btn

        raise NoSuchElementException(f"{row_index} 행에서 상태 아이콘을 찾을 수 없음")

    # 생성된 캠페인 리스트
    def get_cam_list_item(self, cam_name):
        return self.driver.find_element(By.XPATH, f"//p[contains(text(), '{cam_name}')]")

    # 캠페인 정리하기
    def move_all_running_to_pause(self, timeout=10, max_loops=50):
        wait = WebDriverWait(self.driver, timeout)

        for _ in range(max_loops):
            rows = self.driver.find_elements(*self.grid_rows)
            if not rows:
                return

            before_count = len(rows)
            row = rows[0]

            try:
                btn = row.find_element(
                    By.XPATH,
                    ".//button[.//*[name()='svg' and (@data-testid='PlayArrowIcon' or @data-testid='PauseOutlinedIcon')]]"
                )
            except NoSuchElementException:
                btn = GroobeeActions.click_status_icon_by_name(row, self.driver)

            wait.until(lambda d: btn.is_displayed() and btn.is_enabled())
            btn.click()

            BaseClass.wait_clickable(self.driver, self.status_icon_confirm, timeout).click()

            # row 개수 감소(또는 0)
            wait.until(lambda d: len(d.find_elements(*self.grid_rows)) < before_count)

        raise TimeoutException("진행중 캠페인을 모두 중지중으로 이동하지 못했습니다. (max_loops 초과)")

    # 캠페인 정리하기 검증
    def assert_no_running_campaigns(self, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: len(d.find_elements(*self.grid_rows)) == 0
            )
        except TimeoutException:
            count = len(self.driver.find_elements(*self.grid_rows))
            assert False, f"진행중 캠페인이 남아있음: {count}개"