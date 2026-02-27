import platform
import time
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
from datetime import datetime, timedelta

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
    single_tab = (By.XPATH, "//button[contains(text(),'단일 발송')]")
    repeat_tab = (By.XPATH, "//button[contains(text(),'반복 발송')]")
    complete_tab = (By.XPATH, "//button[contains(text(),'발송 완료')]")

    # 상태 아이콘
    status_icon_play = (By.XPATH, "//div[@class='MuiDataGrid-row']//button[.//*[name()='svg' and @data-testid='PlayArrowIcon']]")
    status_icon_pause = (By.XPATH, "//div[@class='MuiDataGrid-row']//button[.//*[name()='svg' and @data-testid='PauseOutlinedIcon']]")
    status_icon_cancel = (By.XPATH, "//button[contains(text(),'취소')]")
    status_icon_confirm = (By.XPATH, "//button[contains(text(),'확인')]")

    # 리스트 아이콘
    search_icon=(By.XPATH, "//button[@data - testid = 'SearchIcon']")

    # 관리 도구
    tools_icon = (By.XPATH, "//div[@class='MuiDataGrid-row']//button[.//*[name()='svg' and @data-testid='MoreHorizIcon']]")
    modify_icon = (By.XPATH, "//li[@role='menuitem' and .//*[normalize-space()='수정']]")
    copy_icon = (By.XPATH, "//li[@role='menuitem' and .//*[normalize-space()='복사']]")
    download_icon = (By.XPATH, "//li[@role='menuitem' and .//*[normalize-space()='방문자 리스트 다운로드']]")
    report_icon = (By.XPATH, "//li[@role='menuitem' and .//*[normalize-space()='분석 리포트']]")
    view_icon = (By.XPATH, "//li[@role='menuitem' and .//*[normalize-space()='미리보기']]")
    exclusion_icon = (By.XPATH, "//li[@role='menuitem' and .//*[normalize-space()='제외 조건 설정']]")
    code_copy_icon = (By.XPATH, "//li[@role='menuitem' and .//*[normalize-space()='코드 샘플 복사']]")
    moveto_storage = (By.XPATH, "//li[@role='menuitem' and .//*[normalize-space()='보관함으로 이동']]")
    moveto_complete = (By.XPATH, "//li[@role='menuitem' and .//*[normalize-space()='완료 탭으로 이동']]")
    delete_icon = (By.XPATH, "//li[@role='menuitem' and .//*[normalize-space()='삭제']]")
    delete_icon_cancel = (By.XPATH, "//button[contains(text(),'취소')]")
    delete_icon_confirm = (By.XPATH, "//button[contains(text(),'확인')]")
    delete_icon_delete = (By.XPATH, "//button[contains(text(),'삭제')]")

    # 세그먼트 불러오기 RNB
    target_set = (By.XPATH, "//h6[contains(text(),'타겟 설정')]")
    seg_load = (By.XPATH, "//button[contains(text(),'세그먼트 불러오기')]")
    seg_load_push = (By.XPATH, "//button[normalize-space()='세그먼트 불러오기']")
    seg_input = (By.XPATH, "//input[@placeholder='세그먼트명 검색']")
    seg_search_icon = (By.XPATH, "//span[normalize-space()='search_filled']")
    aiseg_tab = (By.XPATH, "//button[@id='basic-tab-0']")
    seg_tab = (By.XPATH, "//button[@id='basic-tab-1']")
    selectBtn = (By.XPATH, "//div[contains(@class,'MuiDialog')]//button[normalize-space()='선택']")

    # 예상 타겟 수
    target_numBtn = (By.XPATH, "//button[contains(text(),'확인하기')]")
    target_num_reBtn = (By.XPATH, "//button[contains(text(),'다시 확인하기')]")
    target_result = (By.XPATH, "//p[contains(., '타겟 수는 변동될 수 있습니다')]")
    target_result_pushNoti = (By.XPATH, "//p[contains(., '예상 타겟 수는')]")

    # 파일 업로드 RNB
    file_uploadBtn = (By.XPATH, "//button[contains(text(),'파일 업로드')]")
    file_input = (By.XPATH, "//input[@type='file']")
    doneBtn = (By.XPATH, "//button[contains(text(),'확인')]")
    doneBtn_pushNoti = (By.XPATH, "//div[contains(@class,'MuiDialogActions')]//button[.//text()[contains(.,'확인')]]")

    # 스케줄 (추가 필요)

    singleBtn = (By.XPATH, "//span[contains(text(),'단일 발송')]")
    repeatBtn = (By.XPATH, "//span[contains(text(),'반복 발송')]")
    repeat_endBtn = (By.XPATH, "//span[contains(text(),'수동 종료 전까지')]")
    repeat_setBtn = (By.XPATH, "//span[contains(text(),'기간 지정')]")
    repeat_setBtn_input = (By.XPATH, "//input[@placeholder='YYYY.MM.DD ~ YYYY.MM.DD']")
    repeat_cycleBtn = (By.XPATH, "//button[contains(text(),'설정하기')]")
    repeat_cycle_num_bx = (By.XPATH, "//div[normalize-space()='1']")
    edit_repeat_cycle_num_bx = (By.XPATH, "//div[@role='combobox' and contains(@class,'MuiSelect-select')]")
    repeat_cycle_num_1 = (By.XPATH, "//li[normalize-space()='1']")
    repeat_cycle_num_2 = (By.XPATH, "//li[normalize-space()='2']")
    repeat_cycle_num_3 = (By.XPATH, "//li[normalize-space()='3']")
    repeat_cycle_num_4 = (By.XPATH, "//li[normalize-space()='4']")
    repeat_cycle_num_5 = (By.XPATH, "//li[normalize-space()='5']")
    repeat_cycle_every_bx = (By.XPATH, "//div[contains(text(),'일마다')]")
    repeat_cycle_every_day = (By.XPATH, "//li[contains(text(),'일마다')]")
    repeat_cycle_every_week = (By.XPATH, "//li[contains(text(),'주마다')]")
    repeat_cycle_every_week_sun = (By.XPATH, "(//div[contains(@role,'button')])[1]")
    repeat_cycle_every_week_mon = (By.XPATH, "(//div[contains(@role,'button')])[2]")
    repeat_cycle_every_week_tue = (By.XPATH, "(//div[contains(@role,'button')])[3]")
    repeat_cycle_every_week_wed = (By.XPATH, "(//div[contains(@role,'button')])[4]")
    repeat_cycle_every_week_thu = (By.XPATH, "(//div[contains(@role,'button')])[5]")
    repeat_cycle_every_week_fri = (By.XPATH, "(//div[contains(@role,'button')])[6]")
    repeat_cycle_every_week_sat = (By.XPATH, "(//div[contains(@role,'button')])[7]")
    repeat_cycle_every_month = (By.XPATH, "//li[contains(text(),'개월마다')]")
    repeat_cycle_every_month_date_bx = (By.XPATH, "//div[normalize-space()='1일']")
    repeat_cycle_every_month_date_1 = (By.XPATH, "//li[normalize-space()='1일']")
    # 2일 ~ 31일 필요 시 작성
    repeat_cycle_every_month_date_end = (By.XPATH, "//li[normalize-space()='말일']")
    date_input = (By.XPATH, "//input[@placeholder='YYYY.MM.DD hh:mm']")
    time_input = (By.XPATH, "//input[@placeholder='hh:mm']")

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
        # 만들기 화면 진입 대기
        self.wait_url_contains("/regist", timeout)

    # 온사이트 캠페인/푸시 알림 캠페인 만들기 버튼
    def click_create_pushnoti_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.createBtn, timeout).click()

    # 캠페인 생성
    def send_cam_name(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.cam_name, timeout)
        modifier = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
        el.click()
        el.send_keys(modifier, "a")
        el.send_keys(Keys.BACKSPACE)
        el.send_keys(text)
    # 푸시 알림 캠페인 - 제목 수정
    def send_cam_name_push(self, locator, value, timeout=10):
        el = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        el.click()
        self.driver.execute_script(
            """
            const element = arguments[0];
            element.value = '';
            element.dispatchEvent(new Event('input', { bubbles: true }));
            """,
            el
        )
        self.driver.execute_script(
            """
            const element = arguments[0];
            const value = arguments[1];
            element.value = value;
            element.dispatchEvent(new Event('input', { bubbles: true }));
            element.dispatchEvent(new Event('change', { bubbles: true }));
            """,
            el,
            value
        )
        el.send_keys(Keys.SPACE)
        el.send_keys(Keys.BACKSPACE)

    def send_cam_des(self, text, timeout=10):
        el = BaseClass.wait_visible(self.driver, self.cam_des, timeout)
        el.clear()
        el.send_keys(text)

    # 푸시 알림 캠페인 - 상세 설명 수정
    def send_cam_des_push(self, locator, value, timeout=10):
        el = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )
        el.click()
        self.driver.execute_script(
            """
            const element = arguments[0];
            element.value = '';
            element.dispatchEvent(new Event('input', { bubbles: true }));
            """,
            el
        )
        self.driver.execute_script(
            """
            const element = arguments[0];
            const value = arguments[1];
            element.value = value;
            element.dispatchEvent(new Event('input', { bubbles: true }));
            element.dispatchEvent(new Event('change', { bubbles: true }));
            """,
            el,
            value
        )
        el.send_keys(Keys.SPACE)
        el.send_keys(Keys.BACKSPACE)

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
        time.sleep(1.5)
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
    def click_single_tab(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.single_tab, timeout).click()
    def click_repeat_tab(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_tab, timeout).click()
    def click_complete_tab(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.complete_tab, timeout).click()

    # 상태 아이콘
    def click_status_icon_play(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.status_icon_play, timeout).click()
    def click_status_icon_pause(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.status_icon_pause, timeout).click()
    def click_status_icon_cancel(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.status_icon_cancel, timeout).click()
    def click_status_icon_confirm(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.status_icon_confirm, timeout).click()

    # 서치 아이콘
    def click_search_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.search_icon, timeout).click()

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
    def click_moveto_complete_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.moveto_complete, timeout).click()
    def click_delete_icon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.delete_icon, timeout).click()
    def click_delete_icon_cancel(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.delete_icon_cancel, timeout).click()
    def click_delete_icon_confirm(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.delete_icon_confirm, timeout).click()
    def click_delete_icon_delete(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.delete_icon_delete, timeout).click()

    # 세그먼트 불러오기 RNB
    def click_target_set(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.target_set, timeout).click()
    def click_seg_load(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.seg_load, timeout).click()

    def click_seg_load_push(self, timeout=10):
        BaseClass.wait_overlay_gone(self.driver, timeout)

        el = BaseClass.wait_clickable(self.driver, self.seg_load_push, timeout)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        el.click()

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
    def click_target_pushnoti_num_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver,self.target_numBtn, timeout).click()
        BaseClass.wait_visible(self.driver, self.target_result_pushNoti, 20)

    # 파일 업로드 RNB
    def click_file_upload_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.file_uploadBtn, timeout).click()
    def send_file_input(self, file, timeout=10):
        file_path = BaseClass.getdata_file(file)
        el = BaseClass.wait_visible(self.driver, self.file_input, timeout)
        el.send_keys(file_path)
    def click_done_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.doneBtn, timeout).click()
    def click_done_btn_pushnoti(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.doneBtn_pushNoti, timeout).click()

    # 스케줄 (추가 필요)
    def click_single_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.singleBtn, timeout).click()
    def click_repeat_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeatBtn, timeout).click()
    def click_repeat_end_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_endBtn, timeout).click()
    def click_repeat_set_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_setBtn, timeout).click()
    def send_repeat_set_btn_input(self, text, timeout=10):
        el = BaseClass.wait_clickable(self.driver, self.repeat_setBtn_input, timeout)
        el.clear()
        el.send_keys(text)
    def click_cycle_btn(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycleBtn, timeout).click()
    def click_cycle_num_bx(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_num_bx, timeout).click()
    def edit_click_cycle_num_bx(self, timeout=10):
        el = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.edit_repeat_cycle_num_bx)
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", el
        )
        self.driver.execute_script("arguments[0].click();", el)

    def edit_click_cycle_num_1(self, timeout=10):
        # dropdown 열려 있는지 대기
        el = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.repeat_cycle_num_1)
        )
        self.driver.execute_script("arguments[0].click();", el)


    def click_cycle_num_1(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_num_1, timeout).click()
    def click_cycle_num_2(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_num_2, timeout).click()
    def click_cycle_num_3(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_num_3, timeout).click()
    def click_cycle_num_4(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_num_4, timeout).click()
    def click_cycle_num_5(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_num_5, timeout).click()
    def click_repeat_cycle_every_bx(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_every_bx, timeout).click()
    def click_repeat_cycle_every_day(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_every_day, timeout).click()
    def click_repeat_cycle_every_week(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_every_week, timeout).click()
    def click_repeat_cycle_every_week_sun(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_every_week_sun, timeout).click()
    def click_repeat_cycle_every_week_mon(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_every_week_mon, timeout).click()
    def click_repeat_cycle_every_week_tue(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_every_week_tue, timeout).click()
    def click_repeat_cycle_every_week_wed(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_every_week_wed, timeout).click()
    def click_repeat_cycle_every_week_thu(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_every_week_thu, timeout).click()
    def click_repeat_cycle_every_week_fri(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_every_week_fri, timeout).click()
    def click_repeat_cycle_every_week_sat(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_every_week_sat, timeout).click()
    def click_repeat_cycle_every_month(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_every_month, timeout).click()
    def click_repeat_cycle_every_month_date_bx(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_every_month_date_bx, timeout).click()
    def click_repeat_cycle_every_month_date_1(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_every_month_date_1, timeout).click()
    # 2일 ~ 31일 필요 시 작성
    def click_repeat_cycle_every_month_date_end(self, timeout=10):
        BaseClass.wait_clickable(self.driver, self.repeat_cycle_every_month_date_end, timeout).click()

    # 발송 일시 > 현재 시간 +n분 입력
    def send_date_input(self, minutes_from_now=5, timeout=10):
        el = BaseClass.wait_clickable(self.driver, self.date_input, timeout)
        dt = datetime.now() + timedelta(minutes=minutes_from_now)
        text = dt.strftime("%Y.%m.%d %H:%M")

        modifier = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
        el.send_keys(modifier, "a")
        el.send_keys(Keys.BACKSPACE)
        el.send_keys(text)
        el.send_keys(Keys.ESCAPE)

    # 발송 일시 > 현재 시간 +n분 일치 확인
    def is_date_input_match(self, minutes=5, tolerance_minutes=1, timeout=5):
        el = BaseClass.wait_visible(self.driver, self.date_input, timeout)
        value = el.get_attribute("value").strip()

        try:
            actual = datetime.strptime(value, "%Y.%m.%d %H:%M")
        except ValueError:
            return False

        expected = datetime.now() + timedelta(minutes=minutes)
        diff_seconds = abs((actual - expected).total_seconds())

        return diff_seconds <= tolerance_minutes * 60

    # 발송 시간 > 현재 시간 +n분 입력
    def send_time_input(self, minutes_from_now=5, timeout=10):
        el = BaseClass.wait_clickable(self.driver, self.time_input, timeout)
        dt = datetime.now() + timedelta(minutes=minutes_from_now)
        text = dt.strftime("%H:%M")

        modifier = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
        el.send_keys(modifier, "a")
        el.send_keys(Keys.BACKSPACE)
        el.send_keys(text)
        el.send_keys(Keys.ESCAPE)

    # 발송 시간 > 현재 시간 +n분 일치 확인
    def is_time_input_match(self, minutes=5, tolerance_minutes=1, timeout=5):
        el = BaseClass.wait_visible(self.driver, self.time_input, timeout)
        value = el.get_attribute("value").strip()

        try:
            actual_t = datetime.strptime(value, "%H:%M").time()
        except ValueError:
            return False

        expected_dt = datetime.now() + timedelta(minutes=minutes)
        expected_t = expected_dt.time()

        # time만 비교하면 자정 넘어갈 때 애매해질 수 있어서 "오늘 날짜"로 붙여서 diff 계산
        base = datetime.now().date()
        actual_dt = datetime.combine(base, actual_t)
        expected_dt2 = datetime.combine(base, expected_t)

        diff_seconds = abs((actual_dt - expected_dt2).total_seconds())

        # 자정 근처 보정(예: 23:59 vs 00:01 같은 케이스)
        diff_seconds = min(diff_seconds, 24 * 3600 - diff_seconds)

        return diff_seconds <= tolerance_minutes * 60

    # 반복 주기 텍스트 확인
    def is_repeat_cycle_text_visible(self, text, timeout=5):
        locator = (By.XPATH, f"//p[contains(normalize-space(), '{text}')]")
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

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
        cam_element = self.get_cam_item(cam_name)

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
        cam_element = self.get_cam_item(cam_name)

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
        cam_element = self.get_cam_item(cam_name)

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

    # 생성된 캠페인
    def get_cam_item(self, cam_name):
        return self.driver.find_element(By.XPATH, f"//p[contains(text(), '{cam_name}')]")

    # 생성된 캠페인 리스트
    def get_cam_list_items(self, cam_name):
        return self.driver.find_elements(By.XPATH, f"//p[contains(text(), '{cam_name}')]")

    # 완료 탭으로 이동
    def moveto_complete_by_name(self, text):
        while True:
            items = self.get_cam_list_items(text)
            if not items:
                break

            cam_name = items[0].text

            try:
                self.click_tools_icon_by_name(cam_name)
                self.click_moveto_complete_icon()
                self.click_done_btn()
                BaseClass.wait_overlay_gone(self.driver, 5)
                time.sleep(2)

            except StaleElementReferenceException:
                continue

    # 캠페인 삭제
    def delete_campaign_by_name(self, text):
        while True:
            items = self.get_cam_list_items(text)
            if not items:
                break

            cam_name = items[0].text

            try:
                self.click_tools_icon_by_name(cam_name)
                self.click_delete_icon()
                # 삭제 버튼 or 확인 버튼 누르기
                if not BaseClass.click_if_present(self.driver, self.delete_icon_delete, timeout=1):
                    BaseClass.click_if_present(self.driver, self.delete_icon_confirm, timeout=1)

                BaseClass.wait_overlay_gone(self.driver, 5)
                time.sleep(2)

            except StaleElementReferenceException:
                continue

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