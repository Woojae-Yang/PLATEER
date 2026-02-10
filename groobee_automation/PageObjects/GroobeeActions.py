from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

    # 만들기 버튼
    createBtn = (By.XPATH, "//button[contains(text(),'만들기')]")

    # 캠페인 생성
    cam_name = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 40자']")
    cam_des = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 400자']")

    # 태그 추가
    addtagBtn = (By.XPATH, "//button[contains(text(),'태그 추가')]")
    tag_input = (By.XPATH, "//textarea[@id='downshift-multiple-input']")
    order_frequency_tab = (By.XPATH, "//button[@id='basic-tab-0']")
    order_ganada_tab = (By.XPATH, "//button[@id='basic-tab-1']")
    tag_cancel = (By.XPATH, "//button[contains(text(),'취소')]")
    tag_add = (By.XPATH, "//div[@role='dialog']//button[normalize-space()='추가']")

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
    modify_icon = (By.XPATH, "//p[contains(text(),'수정')]")
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

    # 세그먼트 불러오기 RNB
    target_set = (By.XPATH, "//h6[contains(text(),'타겟 설정')]")
    seg_load = (By.XPATH, "//button[contains(text(),'세그먼트 불러오기')]")
    seg_input = (By.XPATH, "//input[@placeholder='세그먼트명 검색']")
    seg_search_icon = (By.XPATH, "//span[normalize-space()='search_filled']")
    aiseg_tab = (By.XPATH, "//button[@id='basic-tab-0']")
    seg_tab = (By.XPATH, "//button[@id='basic-tab-1']")
    selectBtn = (By.XPATH, "//div[contains(@class,'MuiDialog')]//button[normalize-space()='선택']")

    # 예상 타겟 수
    target_numBtn = (By.XPATH, "//button[contains(text(),'확인하기')]")
    target_num_reBtn = (By.XPATH, "//button[contains(text(),'다시 확인하기')]")
    target_result = (By.XPATH, "//p[contains(., '타겟 수는 변동될 수 있습니다')]")

    # 파일 업로드 RNB
    file_uploadBtn = (By.XPATH, "//button[contains(text(),'파일 업로드')]")
    file_input = (By.XPATH, "//input[@type='file']")
    doneBtn = (By.XPATH, "//button[contains(text(),'확인')]")

    # 완료
    cancelBtn = (By.XPATH, "//button[contains(text(),'취소')]")
    nextBtn = (By.XPATH, "//button[contains(text(),'다음 단계')]")
    saveBtn = (By.XPATH, "//button[contains(text(),'저장')]")

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

    # 만들기 버튼
    def click_create_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.createBtn, timeout).click()
        self.wait_url_contains("/regist", timeout)

    # 캠페인 생성
    def send_cam_name(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.cam_name, timeout)
        el.click()
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(Keys.BACKSPACE)
        el.send_keys(text)
    def send_cam_des(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.cam_des, timeout)
        el.click()
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(Keys.BACKSPACE)
        el.send_keys(text)
    def get_cam_name(self, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.cam_name, timeout)
        return el.get_attribute("value")
    def get_cam_des(self, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.cam_des, timeout)
        return el.get_attribute("value")

    # 태그 추가
    def click_addtag_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.addtagBtn, timeout).click()
    def send_tag_input(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.tag_input, timeout)
        el.clear()
        el.send_keys(text)
        el.send_keys(Keys.ENTER)
    def click_order_frequency_tab(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.order_frequency_tab, timeout).click()
    def click_order_ganada_tab(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.order_ganada_tab, timeout).click()
    def click_tag_cancel(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.tag_cancel, timeout).click()
    def click_tag_add(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.tag_add, timeout).click()
    def wait_tag_visible(self, tag_text, timeout=10):
        locator = (By.XPATH, f"//span[contains(normalize-space(.), '{tag_text}')]")
        return BaseClass.wait_visible(self.driver, locator, timeout)

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
    def click_modify_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.modify_icon, timeout).click()
        self.wait_url_contains("/regist", timeout)
    def click_copy_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.copy_icon, timeout).click()
        self.wait_url_contains("/regist", timeout)
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

    # 세그먼트 불러오기 RNB
    def click_target_set(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.target_set, timeout).click()
    def click_seg_load(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_load, timeout).click()
    def send_seg_input(self, text, timeout=10):
        el = BaseClass.wait_clickable(self.driver, self.seg_input, timeout)
        el.clear()
        el.send_keys(text)
    def click_seg_search_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_search_icon, timeout).click()
    def click_aiseg_tab(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.aiseg_tab, timeout).click()
    def click_seg_tab(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_tab, timeout).click()
    def click_select_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.selectBtn, timeout).click()

    # 예상 타겟 수
    def wait_target_num_btn_clickable(self, timeout=10):
        return BaseClass.wait_clickable(self.driver, self.target_numBtn, timeout)
    def click_target_num_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.target_numBtn, timeout).click()
        BaseClass.wait_visible(self.driver, self.target_result, 20)
    def wait_target_num_re_btn_visible(self, timeout=10):
        return BaseClass.wait_visible(self.driver, self.target_numBtn, timeout)
    def click_target_num_re_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.target_num_reBtn, timeout).click()
        BaseClass.wait_visible(self.driver, self.target_result, 20)

    # 파일 업로드 RNB
    def click_file_upload_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.file_uploadBtn, timeout).click()
    def send_file_input(self, file, timeout=10):
        file_path = BaseClass.getdata_file(file)
        el = BaseClass.wait_visible(self.driver, self.file_input, timeout)
        el.send_keys(file_path)
    def click_done_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.doneBtn, timeout).click()

    # 완료
    def click_cancel_btn(self, timeout=10):
        el = BaseClass.wait_clickable(self.driver, self.cancelBtn, timeout)
        try:
            el.click()
        except (ElementClickInterceptedException, WebDriverException):
            self.driver.execute_script("arguments[0].click();", el)
    def click_next_btn(self, timeout=10):
        el = BaseClass.wait_clickable(self.driver, self.nextBtn, timeout)
        try:
            el.click()
        except (ElementClickInterceptedException, WebDriverException):
            self.driver.execute_script("arguments[0].click();", el)
    def click_save_btn(self, timeout=10):
        el = BaseClass.wait_clickable(self.driver, self.saveBtn, timeout)
        try:
            el.click()
        except (ElementClickInterceptedException, WebDriverException):
            self.driver.execute_script("arguments[0].click();", el)

    # 관리 도구 클릭
    def click_tools_icon_by_name(self, cam_name):
        cam_element = self.get_cam_list_item(cam_name)

        row = cam_element.find_element(
            By.XPATH, "./ancestor-or-self::div[contains(@class,'MuiDataGrid-row')]"
        )
        row_index = row.get_attribute("data-rowindex")

        pinned_container = self.driver.find_element(
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
                btn.click()
                return

    # 중지중 아이콘 클릭
    def click_pause_icon_by_name(self, cam_name):
        cam_element = self.get_cam_list_item(cam_name)

        row = cam_element.find_element(
            By.XPATH, "./ancestor-or-self::div[contains(@class,'MuiDataGrid-row')]"
        )
        row_index = row.get_attribute("data-rowindex")

        try:
            btn = row.find_element(
                By.XPATH,
                ".//button[.//*[name()='svg' and @data-testid='PauseOutlinedIcon']]"
            )
            btn.click()
            return
        except NoSuchElementException:
            pass

        pinned_container = self.driver.find_element(
            By.XPATH, "//div[contains(@class,'MuiDataGrid-pinnedColumns--right')]"
        )
        buttons = pinned_container.find_elements(
            By.XPATH,
            ".//button[.//*[name()='svg' and @data-testid='PauseOutlinedIcon']]"
        )

        for btn in buttons:
            btn_row = btn.find_element(
                By.XPATH, "./ancestor-or-self::div[contains(@class,'MuiDataGrid-row')]"
            )
            if btn_row.get_attribute("data-rowindex") == row_index:
                btn.click()
                return

    # 진행중 아이콘 클릭
    def click_play_icon_by_name(self, cam_name):
        cam_element = self.get_cam_list_item(cam_name)

        row = cam_element.find_element(
            By.XPATH, "./ancestor-or-self::div[contains(@class,'MuiDataGrid-row')]"
        )
        row_index = row.get_attribute("data-rowindex")

        try:
            btn = row.find_element(
                By.XPATH,
                ".//button[.//*[name()='svg' and @data-testid='PlayArrowIcon']]"
            )
            btn.click()
            return
        except NoSuchElementException:
            pass

        pinned_container = self.driver.find_element(
            By.XPATH, "//div[contains(@class,'MuiDataGrid-pinnedColumns--right')]"
        )
        buttons = pinned_container.find_elements(
            By.XPATH,
            ".//button[.//*[name()='svg' and @data-testid='PlayArrowIcon']]"
        )

        for btn in buttons:
            btn_row = btn.find_element(
                By.XPATH, "./ancestor-or-self::div[contains(@class,'MuiDataGrid-row')]"
            )
            if btn_row.get_attribute("data-rowindex") == row_index:
                btn.click()
                return

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