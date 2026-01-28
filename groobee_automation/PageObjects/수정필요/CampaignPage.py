from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException

class CampaignPage:

    def __init__(self, driver):
        self.driver = driver

    # -------------------------element 선언 영역-------------------------
    # LNB
    dashboardMenu = (By.XPATH, "//p[contains(text(),'대시보드')]")
    campaignMenu = (By.XPATH, "//p[contains(text(),'온사이트 캠페인')]")

    # 만들기
    createBtn = (By.XPATH, "//button[contains(text(),'만들기')]")
    createBtn_onsite = (By.XPATH, "//li[contains(text(),'온사이트 캠페인')]")
    createBtn_inapp = (By.XPATH, "//li[contains(text(),'인앱 메시지 캠페인')]")

    # 상태탭
    progress_tab = (By.XPATH, "//button[contains(text(),'진행중')]")
    pause_tab = (By.XPATH, "//button[contains(text(),'중지중')]")
    storage_tab = (By.XPATH, "//button[contains(text(),'보관함')]")

    # 상태
    status_icon_play = (By.XPATH,"//div[@class='MuiDataGrid-row']//button[.//*[name()='svg' and @data-testid='PlayArrowIcon']]")
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

    # 캠페인 입력
    cam_title = (By.XPATH, "//h1[contains(text(),'새로운 온사이트 캠페인 만들기')]")
    cam_name = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 40자']")
    cam_des = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 400자']")

    # 접속 유형
    type_pcweb = (By.XPATH, "//input[@value='PC']")
    type_mobile = (By.XPATH, "//input[@value='MO']")
    type_mobile_web = (By.XPATH, "//input[@value='MW']")
    type_mobile_app = (By.XPATH, "//input[@value='MA']")

    # 타겟 설정
    seg_load = (By.XPATH, "//button[contains(text(),'세그먼트 불러오기')]")

    # 세그먼트 불러오기 RNB(설정할 값 실제 작성)
    aiseg_tab = (By.XPATH, "//button[@id='basic-tab-0']")
    seg_tab = (By.XPATH, "//button[@id='basic-tab-1']")
    now_pc_seg = (By.XPATH, "//h6[contains(text(),'[QA] 온사이트웹-현재-PC접속 테스트 세그먼트')]")
    now_os_seg = (By.XPATH, "//h6[contains(text(),'[QA] 온사이트네이티브-현재-접속OS 테스트 세그먼트')]")
    selectBtn = (By.XPATH, "//button[contains(text(),'선택')]")

    # 추가
    addBtn = (By.XPATH, "//button[contains(text(),'추가')]")
    a_type = (By.XPATH, "//button[contains(text(),'A안')]")
    b_type = (By.XPATH, "//button[contains(text(),'B안')]")
    c_type = (By.XPATH, "//button[contains(text(),'C안')]")
    d_type = (By.XPATH, "//button[contains(text(),'D안')]")
    e_type = (By.XPATH, "//button[contains(text(),'E안')]")
    type_del_icon = (By.XPATH, "(//button[@type='button'])[11]")

    # 디자인 유형
    design_popup = (By.XPATH, "//input[@value='POPUP']")
    design_sticky_default = (By.XPATH, "//input[@value='STICKY_DEFAULT']")
    design_sticky_btn = (By.XPATH, "//input[@value='STICKY_BUTTON']")

    # 파일 업로드 RNB
    file_uploadBtn = (By.XPATH, "//button[contains(text(),'파일 업로드')]")
    file_input = (By.XPATH, "//input[@type='file']")
    doneBtn = (By.XPATH, "//button[contains(text(),'확인')]")

    # URL 입력
    input_url = (By.XPATH, "//textarea[@placeholder='http:// 또는 https://를 포함한 URL']")
    image_map = (By.XPATH, "//input[@value='image-map']")

    # 내용 입력
    desBtn = (By.XPATH, "(//input[@type='checkbox'])[5]")
    input_des = (By.XPATH, "//textarea[@placeholder='한글 공백 포함 최대 80자']")
    sort_des = (By.XPATH, "(//button[@value='center'])[2]")
    input_txt20 = (By.XPATH, "//textarea[@placeholder='한글 공백 포함 최대 20자']")
    input_txt16 = (By.XPATH, "//textarea[@placeholder='한글 공백 포함 최대 16자']")
    input_txt40 = (By.XPATH, "//textarea[@placeholder='한글 공백 포함 최대 40자']")
    input_txt15 = (By.XPATH, "//textarea[@placeholder='한글 공백 포함 최대 15자']")
    bold_cbx = (By.XPATH, "(//input[@type='checkbox'])[1]")
    bold_cbx2 = (By.XPATH, "(//input[@type='checkbox'])[2]")
    bold_cbx3 = (By.XPATH, "(//input[@type='checkbox'])[3]")
    sort_mid = (By.XPATH, "//button[@value='1']")
    set_top = (By.XPATH, "//input[@value='48']")
    set_bottom = (By.XPATH, "//input[@value='80']")

    # 노출 위치 설정
    set_tl = (By.XPATH, "//input[@value='TL']")
    set_ml = (By.XPATH, "//input[@value='ML']")
    set_bl = (By.XPATH, "//input[@value='BL']")
    set_tc = (By.XPATH, "//input[@value='TC']")
    set_mc = (By.XPATH, "//input[@value='MC']")
    set_bc = (By.XPATH, "//input[@value='BC']")
    set_tr = (By.XPATH, "//input[@value='TR']")
    set_mr = (By.XPATH, "//input[@value='MR']")
    set_br = (By.XPATH, "//input[@value='BR']")

    # 아이콘
    icon_style = (By.XPATH, "//button[contains(text(),'스타일 선택')]")

    # 스타일
    corner_style = (By.XPATH, "//input[contains(@name,'antoine')]")

    # A/B/N 테스트 설정
    type_auto = (By.XPATH, "//input[@value='true']")
    target_order = (By.XPATH, "//input[@value='OR']")

    # 스케줄
    period_self = (By.XPATH, "//input[@value='MA']")
    period_set = (By.XPATH, "//input[@value='ET']")
    repeat_false = (By.XPATH, "//input[@value='false']")
    repeat_true = (By.XPATH, "//input[@value='true']")
    repeat_setting = (By.XPATH, "//button[contains(text(),'설정하기')]")
    repeat_setting_done = (By.XPATH, "//button[contains(text(),'확인')]")

    # 노출 옵션
    freq_combx = (By.XPATH, "//div[contains(text(),'매일 1번')]")
    freq_one = (By.XPATH, "//li[contains(text(),'1번')]")
    freq_month = (By.XPATH, "//li[contains(text(),'매월 1번')]")
    freq_week = (By.XPATH, "//li[contains(text(),'매주 1번')]")
    freq_day = (By.XPATH, "//li[contains(text(),'매일 1번')]")
    freq_session = (By.XPATH, "//li[contains(text(),'방문 세션마다')]")
    freq_page = (By.XPATH, "//li[contains(text(),'방문 페이지마다')]")
    freq_etc = (By.XPATH, "//li[contains(text(),'기타')]")
    priority_cb = (By.XPATH, "(//input[@type='checkbox'])[7]")

    # 완료
    cancelBtn = (By.XPATH, "//button[contains(text(),'취소')]")
    nextBtn = (By.XPATH, "//button[contains(text(),'다음 단계')]")
    saveBtn = (By.XPATH, "//button[contains(text(),'저장')]")

    # 몰 바로가기
    admin_icon = (By.XPATH, "/html[1]/body[1]/header[1]/div[1]/div[2]/button[2]")
    goto_mall = (By.XPATH, "//p[contains(text(),'몰 바로가기')]")

    # 서비스 페이지
    cam_popup = (By.XPATH, "(//img[@class='img_999999'])[1]")

    # 대시보드 (조회할 값 실제 작성)
    dashboard_onsite_ranking = (By.XPATH, "//h6[contains(text(),'[QA] PC/웹-페이지반복 테스트 캠페인')]")
    dashboard_onsite_impressions = (By.XPATH, "//h6[contains(text(),'노출 수')]/following-sibling::h6")
    dashboard_onsite_clicks = (By.XPATH, "//h6[contains(text(),'클릭 수')]/following-sibling::h6")
    dashboard_onsite_impressions_tab = (By.XPATH, "(//button[@role='tab'][contains(text(),'노출 수')])[1]")
    dashboard_onsite_clicks_tab = (By.XPATH, "(//button[@role='tab'][contains(text(),'클릭 수')])[1]")

    # -------------------------동작 선언 영역-------------------------
    # LNB
    def click_dashboard_menu(self):
        return self.driver.find_element(*CampaignPage.dashboardMenu)
    def click_campaign_menu(self):
        return self.driver.find_element(*CampaignPage.campaignMenu)

    # 만들기
    def click_create_btn(self):
        return self.driver.find_element(*CampaignPage.createBtn)
    def click_create_btn_onsite(self):
        return self.driver.find_element(*CampaignPage.createBtn_onsite)
    def click_create_btn_inapp(self):
        return self.driver.find_element(*CampaignPage.createBtn_inapp)

    # 상태탭
    def click_progress_tab(self):
        return self.driver.find_element(*CampaignPage.progress_tab)
    def click_pause_tab(self):
        return self.driver.find_element(*CampaignPage.pause_tab)
    def click_storage_tab(self):
        return self.driver.find_element(*CampaignPage.storage_tab)

    # 상태
    def click_status_icon_play(self):
        return self.driver.find_element(*CampaignPage.status_icon_play)
    def click_status_icon_pause(self):
        return self.driver.find_element(*CampaignPage.status_icon_pause)
    def click_status_icon_cancel(self):
        return self.driver.find_element(*CampaignPage.status_icon_cancel)
    def click_status_icon_confirm(self):
        return self.driver.find_element(*CampaignPage.status_icon_confirm)

    # 관리 도구
    def click_tools_icon(self):
        return self.driver.find_element(*CampaignPage.tools_icon)
    def click_update_icon(self):
        return self.driver.find_element(*CampaignPage.update_icon)
    def click_copy_icon(self):
        return self.driver.find_element(*CampaignPage.copy_icon)
    def click_report_icon(self):
        return self.driver.find_element(*CampaignPage.report_icon)
    def click_view_icon(self):
        return self.driver.find_element(*CampaignPage.view_icon)
    def click_exclusion_icon(self):
        return self.driver.find_element(*CampaignPage.exclusion_icon)
    def click_code_copy_icon(self):
        return self.driver.find_element(*CampaignPage.code_copy_icon)
    def click_moveto_storage_icon(self):
        return self.driver.find_element(*CampaignPage.moveto_storage)
    def click_moveto_pause_icon(self):
        return self.driver.find_element(*CampaignPage.moveto_pause)
    def click_delete_icon(self):
        return self.driver.find_element(*CampaignPage.delete_icon)
    def click_delete_icon_cancel(self):
        return self.driver.find_element(*CampaignPage.delete_icon_cancel)
    def click_delete_icon_confirm(self):
        return self.driver.find_element(*CampaignPage.delete_icon_confirm)

    # 삭제할 캠페인 관리 도구 찾기
    @staticmethod
    def click_tools_icon_by_name(cam_element, driver):
        # row 찾기
        row = cam_element.find_element(By.XPATH, "./ancestor::div[contains(@class,'MuiDataGrid-row')]")
        row_index = row.get_attribute("data-rowindex")

        # pinned 영역
        pinned_container = driver.find_element(By.XPATH, "//div[contains(@class,'MuiDataGrid-pinnedColumns--right')]")
        buttons = pinned_container.find_elements(By.XPATH, ".//button[contains(@class,'MuiIconButton-root')]")

        # row index 매칭
        for btn in buttons:
            btn_row = btn.find_element(By.XPATH, "./ancestor::div[contains(@class,'MuiDataGrid-row')]")
            btn_row_index = btn_row.get_attribute("data-rowindex")

            if btn_row_index == row_index:
                return btn

        raise NoSuchElementException(f"{row_index} 행에서 tools 아이콘을 찾을 수 없음")

    # 상태 아이콘 자동 탐지 (진행중/중지중/보관함)
    @staticmethod
    def click_status_icon_by_name(cam_element, driver):
        # row 찾기
        row = cam_element.find_element(
                By.XPATH, "./ancestor::div[contains(@class,'MuiDataGrid-row')]"
            )
        row_index = row.get_attribute("data-rowindex")

        # 1) row 내부에서 Play/Pause 탐색
        try:
            inner_btn = row.find_element(
                By.XPATH,
                ".//button[.//*[name()='svg' and (@data-testid='PlayArrowIcon' or @data-testid='PauseOutlinedIcon')]]"
            )
            return inner_btn
        except NoSuchElementException:
            pass  # row 내부에 없으면 pinned 영역 검사

        # 2) pinned columns 탐색
        try:
            pinned_container = driver.find_element(
                By.XPATH, "//div[contains(@class,'MuiDataGrid-pinnedColumns--right')]"
            )
            status_buttons = pinned_container.find_elements(
                By.XPATH,
                ".//button[.//*[name()='svg' and (@data-testid='PlayArrowIcon' or @data-testid='PauseOutlinedIcon')]]"
            )

            for btn in status_buttons:
                btn_row = btn.find_element(
                    By.XPATH, "./ancestor::div[contains(@class,'MuiDataGrid-row')]"
                )
                btn_row_index = btn_row.get_attribute("data-rowindex")
                if btn_row_index == row_index:
                    return btn
        except NoSuchElementException:
            pass

        raise NoSuchElementException(f"{row_index} 행에서 상태 아이콘을 찾을 수 없음")

    # 캠페인 입력
    def send_cam_name(self):
        return self.driver.find_element(*CampaignPage.cam_name)
    def send_cam_des(self):
        return self.driver.find_element(*CampaignPage.cam_des)

    # 접속 유형
    def click_type_pcweb(self):
        return self.driver.find_element(*CampaignPage.type_pcweb)
    def click_type_mobile(self):
        return self.driver.find_element(*CampaignPage.type_mobile)
    def click_type_mobile_web(self):
        return self.driver.find_element(*CampaignPage.type_mobile_web)
    def click_type_mobile_app(self):
        return self.driver.find_element(*CampaignPage.type_mobile_app)

    # 타겟 설정
    def click_seg_load(self):
        return self.driver.find_element(*CampaignPage.seg_load)

    # 세그먼트 불러오기 RNB(설정할 값 실제 작성)
    def click_aiseg_tab(self):
        return self.driver.find_element(*CampaignPage.aiseg_tab)
    def click_seg_tab(self):
        return self.driver.find_element(*CampaignPage.seg_tab)
    def click_now_pc_seg(self):
        return self.driver.find_elements(*CampaignPage.now_pc_seg)
    def click_now_os_seg(self):
        return self.driver.find_elements(*CampaignPage.now_os_seg)
    def click_select_btn(self):
        return self.driver.find_element(*CampaignPage.selectBtn)

    # 추가
    def click_add_btn(self):
        return self.driver.find_element(*CampaignPage.addBtn)
    def click_a_type(self):
        return self.driver.find_element(*CampaignPage.a_type)
    def click_b_type(self):
        return self.driver.find_element(*CampaignPage.b_type)
    def click_c_type(self):
        return self.driver.find_element(*CampaignPage.c_type)
    def click_d_type(self):
        return self.driver.find_element(*CampaignPage.d_type)
    def click_e_type(self):
        return self.driver.find_element(*CampaignPage.e_type)
    def click_type_del_icon(self):
        return self.driver.find_element(*CampaignPage.type_del_icon)

    # 디자인 유형
    def click_design_popup(self):
        return self.driver.find_element(*CampaignPage.design_popup)
    def click_design_sticky_default(self):
        return self.driver.find_element(*CampaignPage.design_sticky_default)
    def click_design_sticky_btn(self):
        return self.driver.find_element(*CampaignPage.design_sticky_btn)

    # 파일 업로드 RNB
    def click_file_upload_btn(self):
        return self.driver.find_element(*CampaignPage.file_uploadBtn)
    def send_file_input(self):
        return self.driver.find_element(*CampaignPage.file_input)
    def click_done_btn(self):
        return self.driver.find_element(*CampaignPage.doneBtn)

    # URL 입력
    def send_input_url(self):
        return self.driver.find_element(*CampaignPage.input_url)
    def click_image_map(self):
        return self.driver.find_element(*CampaignPage.image_map)

    # 내용 입력
    def click_des_btn(self):
        return self.driver.find_element(*CampaignPage.desBtn)
    def send_input_des(self):
        return self.driver.find_element(*CampaignPage.input_des)
    def click_sort_des(self):
        return self.driver.find_element(*CampaignPage.sort_des)
    def send_input_txt20(self):
        return self.driver.find_element(*CampaignPage.input_txt20)
    def send_input_txt16(self):
        return self.driver.find_element(*CampaignPage.input_txt16)
    def send_input_txt40(self):
        return self.driver.find_element(*CampaignPage.input_txt40)
    def send_input_txt15(self):
        return self.driver.find_element(*CampaignPage.input_txt15)
    def click_bold_cbx(self):
        return self.driver.find_element(*CampaignPage.bold_cbx)
    def click_bold_cbx2(self):
        return self.driver.find_element(*CampaignPage.bold_cbx2)
    def click_bold_cbx3(self):
        return self.driver.find_element(*CampaignPage.bold_cbx3)
    def click_sort_mid(self):
        return self.driver.find_element(*CampaignPage.sort_mid)
    def click_set_top(self):
        return self.driver.find_element(*CampaignPage.set_top)
    def click_set_bottom(self):
        return self.driver.find_element(*CampaignPage.set_bottom)

    # 노출 위치 설정
    def click_set_tl(self):
        return self.driver.find_element(*CampaignPage.set_tl)
    def click_set_ml(self):
        return self.driver.find_element(*CampaignPage.set_ml)
    def click_set_bl(self):
        return self.driver.find_element(*CampaignPage.set_bl)
    def click_set_tc(self):
        return self.driver.find_element(*CampaignPage.set_tc)
    def click_set_mc(self):
        return self.driver.find_element(*CampaignPage.set_mc)
    def click_set_bc(self):
        return self.driver.find_element(*CampaignPage.set_bc)
    def click_set_tr(self):
        return self.driver.find_element(*CampaignPage.set_tr)
    def click_set_mr(self):
        return self.driver.find_element(*CampaignPage.set_mr)
    def click_set_br(self):
        return self.driver.find_element(*CampaignPage.set_br)

    # 아이콘
    def click_icon_style(self):
        return self.driver.find_element(*CampaignPage.icon_style)

    # 스타일
    def click_corner_style(self):
        return self.driver.find_element(*CampaignPage.corner_style)

    # A/B/N 테스트 설정
    def click_type_auto(self):
        return self.driver.find_element(*CampaignPage.type_auto)
    def click_target_order(self):
        return self.driver.find_element(*CampaignPage.target_order)

    # 스케줄
    def click_period_self(self):
        return self.driver.find_element(*CampaignPage.period_self)
    def click_period_set(self):
        return self.driver.find_element(*CampaignPage.period_set)
    def click_repeat_false(self):
        return self.driver.find_element(*CampaignPage.repeat_false)
    def click_repeat_true(self):
        return self.driver.find_element(*CampaignPage.repeat_true)
    def click_repeat_setting(self):
        return self.driver.find_element(*CampaignPage.repeat_setting)
    def click_repeat_setting_done(self):
        return self.driver.find_element(*CampaignPage.repeat_setting_done)

    # 노출 옵션
    def click_freq_combx(self):
        return self.driver.find_element(*CampaignPage.freq_combx)
    def click_freq_one(self):
        return self.driver.find_element(*CampaignPage.freq_one)
    def click_freq_month(self):
        return self.driver.find_element(*CampaignPage.freq_month)
    def click_freq_week(self):
        return self.driver.find_element(*CampaignPage.freq_week)
    def click_freq_day(self):
        return self.driver.find_element(*CampaignPage.freq_day)
    def click_freq_session(self):
        return self.driver.find_element(*CampaignPage.freq_session)
    def click_freq_page(self):
        return self.driver.find_element(*CampaignPage.freq_page)
    def click_freq_etc(self):
        return self.driver.find_element(*CampaignPage.freq_etc)
    def click_priority_cb(self):
        return self.driver.find_element(*CampaignPage.priority_cb)

    # 완료
    def click_cancel_btn(self):
        return self.driver.find_element(*CampaignPage.cancelBtn)
    def click_next_btn(self):
        return self.driver.find_element(*CampaignPage.nextBtn)
    def click_save_btn(self):
        return self.driver.find_element(*CampaignPage.saveBtn)

    # 생성된 캠페인 리스트
    def get_cam_list_item(self, cam_name):
        return self.driver.find_element(By.XPATH, f"//p[contains(text(), '{cam_name}')]")

    # 몰 바로가기
    def click_admin_icon(self):
        return self.driver.find_element(*CampaignPage.admin_icon)
    def click_goto_mall(self):
        return self.driver.find_element(*CampaignPage.goto_mall)

    # 서비스 페이지
    def click_cam_popup(self):
        return self.driver.find_elements(*CampaignPage.cam_popup)

    # 대시 보드
    def is_ranking_campaign_displayed(self):
        try:
            return self.driver.find_element(*CampaignPage.dashboard_onsite_ranking).is_displayed()
        except NoSuchElementException:
            return False
    def get_onsite_impressions(self):
        import re
        elem = self.driver.find_element(*CampaignPage.dashboard_onsite_impressions)
        num = int(re.findall(r'\d+', elem.text)[0])
        return num
    def get_onsite_clicks(self):
        import re
        elem = self.driver.find_element(*CampaignPage.dashboard_onsite_clicks)
        num = int(re.findall(r'\d+', elem.text)[0])
        return num
    def click_dashboard_onsite_impressions_tab(self):
        return self.driver.find_element(*CampaignPage.dashboard_onsite_impressions_tab)
    def click_dashboard_onsite_clicks_tab(self):
        return self.driver.find_element(*CampaignPage.dashboard_onsite_clicks_tab)