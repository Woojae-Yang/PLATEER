from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    TimeoutException,
    JavascriptException,
    WebDriverException,
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
    smsMenu = (By.XPATH, "//p[contains(text(),'SMS 캠페인')]")
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
    download_icon = (By.XPATH, "//div[contains(text(),'방문자 리스트 다운로드')]")
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
    # 페이지 로딩 대기
    def wait_url_contains(self, path, timeout=10):
        WebDriverWait(self.driver, timeout).until(EC.url_contains(path))

    # LNB
    def click_dashboard_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.dashboardMenu, timeout).click()
        self.wait_url_contains("/dashboard", timeout)
    def click_monitoring_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.monitoringMenu, timeout).click()
        self.wait_url_contains("/monitoring", timeout)
    def click_datamonitoring_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.datamonitoringMenu, timeout).click()
        self.wait_url_contains("/dataMonitoring", timeout)
    def click_aisegment_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.aisegmentMenu, timeout).click()
        self.wait_url_contains("/aisegment", timeout)
    def click_segment_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.segmentMenu, timeout).click()
        self.wait_url_contains("/segment", timeout)
    def click_recommend_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.recommendMenu, timeout).click()
        self.wait_url_contains("/recommend", timeout)
    def click_campaign_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.campaignMenu, timeout).click()
        self.wait_url_contains("/campaign", timeout)
    def click_pushnoti_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.pushnotiMenu, timeout).click()
        self.wait_url_contains("/pushNoti", timeout)
    def click_kakaobrand_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.kakaobrandMenu, timeout).click()
        self.wait_url_contains("/kakaoBrand", timeout)
    def click_kakaomoment_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.kakaomomentMenu, timeout).click()
        self.wait_url_contains("/kakaoMoment", timeout)
    def click_kakaoalim_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.kakaoalimMenu, timeout).click()
        self.wait_url_contains("/kakaoAlim", timeout)
    def click_sms_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.smsMenu, timeout).click()
        self.wait_url_contains("/sms", timeout)
    def click_setting_menu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.settingMenu, timeout).click()
        self.wait_url_contains("/setting/menu", timeout)

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
    def click_download_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.download_icon, timeout).click()
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

    # 진행중 아이콘 찾기
    @staticmethod
    def click_play_icon_by_row(row, driver):
        row_index = row.get_attribute("data-rowindex")

        # 1) row 내부 Play
        try:
            return row.find_element(
                By.XPATH,
                ".//button[.//*[local-name()='svg' and @data-testid='PlayArrowIcon']]"
            )
        except NoSuchElementException:
            pass

        # 2) pinned columns fallback
        try:
            pinned_container = driver.find_element(
                By.XPATH, "//div[contains(@class,'MuiDataGrid-pinnedColumns--right')]"
            )
        except NoSuchElementException:
            return None

        buttons = pinned_container.find_elements(
            By.XPATH,
            ".//button[.//*[local-name()='svg' and @data-testid='PlayArrowIcon']]"
        )

        for btn in buttons:
            try:
                btn_row = btn.find_element(
                    By.XPATH, "./ancestor-or-self::div[contains(@class,'MuiDataGrid-row')]"
                )
                if btn_row.get_attribute("data-rowindex") == row_index:
                    return btn
            except StaleElementReferenceException:
                continue

        # 없으면 None
        return None

    # 캠페인 정리하기
    def move_all_running_to_pause(self, timeout=10, max_loops=50, scan_rows=30):
        short_wait = WebDriverWait(self.driver, 3)
        play_btns = (By.XPATH, "//button[.//*[local-name()='svg' and @data-testid='PlayArrowIcon']]")

        def is_actionable_play(play_button) -> bool:
            try:
                if not play_button.is_displayed() or not play_button.is_enabled():
                    return False

                cls = (play_button.get_attribute("class") or "")
                if "Mui-disabled" in cls:
                    return False

                aria_disabled = (play_button.get_attribute("aria-disabled") or "").lower()
                if aria_disabled == "true":
                    return False

                if play_button.get_attribute("disabled") is not None:
                    return False

                pe = self.driver.execute_script(
                    "return window.getComputedStyle(arguments[0]).pointerEvents;", play_button
                )
                if pe == "none":
                    return False

                return True
            except (StaleElementReferenceException, JavascriptException, WebDriverException):
                return False

        def count_actionable_play() -> int:
            cnt = 0
            for b in self.driver.find_elements(*play_btns):
                if is_actionable_play(b):
                    cnt += 1
            return cnt

        for _ in range(max_loops):
            before_play = count_actionable_play()
            if before_play == 0:
                return

            rows = self.driver.find_elements(*self.grid_rows)
            if not rows:
                return

            clicked_one = False

            for row in rows[:scan_rows]:
                # 1) Play 버튼 찾기
                try:
                    btn = row.find_element(
                        By.XPATH,
                        ".//button[.//*[local-name()='svg' and @data-testid='PlayArrowIcon']]"
                    )
                except NoSuchElementException:
                    # fallback: pinned 영역 등
                    try:
                        btn = self.click_play_icon_by_row(row, self.driver)
                    except NoSuchElementException:
                        continue

                if not is_actionable_play(btn):
                    continue

                # 2) 스크롤
                try:
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center', inline:'center'});", btn
                    )
                except (JavascriptException, WebDriverException):
                    pass

                # 3) 클릭
                try:
                    btn.click()
                except (ElementClickInterceptedException, StaleElementReferenceException, WebDriverException):
                    continue

                # 4) 확인 팝업 클릭
                try:
                    BaseClass.wait_clickable(self.driver, self.status_icon_confirm, timeout).click()
                except TimeoutException:
                    continue
                except WebDriverException:
                    continue

                # 5) 갱신 트리거
                try:
                    self.driver.execute_script("document.body.click();")
                except (JavascriptException, WebDriverException):
                    pass

                # 6) 갱신 확인(실패해도 멈추지 않음)
                try:
                    short_wait.until(lambda _d: count_actionable_play() < before_play)
                except TimeoutException:
                    pass
                except WebDriverException:
                    pass

                clicked_one = True
                break

            # 이번 루프에서 클릭을 하나도 못했으면 종료(무한대기 방지)
            if not clicked_one:
                return

        raise TimeoutException("진행중 캠페인을 모두 중지 처리하지 못했습니다. (max_loops 초과)")