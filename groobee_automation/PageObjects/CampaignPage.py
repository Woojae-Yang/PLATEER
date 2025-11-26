from selenium.webdriver.common.by import By

class CampaignPage:

    def __init__(self, driver):
        self.driver = driver

    # -------------------------element 선언 영역-------------------------
    # 온사이트 캠페인 메뉴
    campaignMenu = (By.XPATH, "//p[contains(text(),'온사이트 캠페인')]")

    # 만들기
    createBtn = (By.XPATH, "//button[contains(text(),'만들기')]")

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
    update_icon = (By.XPATH, "//div[contains(text(),'수정')]")
    copy_icon = (By.XPATH, "//div[contains(text(),'복사')]")
    report_icon = (By.XPATH, "//div[contains(text(),'분석 리포트')]")
    view_icon = (By.XPATH, "//div[contains(text(),'미리보기')]")
    exclusion_icon = (By.XPATH, "//div[contains(text(),'제외 조건 설정')]")
    code_copy_icon = (By.XPATH, "//div[contains(text(),'코드 복사')]")
    moveto_storage = (By.XPATH, "//div[contains(text(),'보관함으로 이동')]")
    moveto_pause = (By.XPATH, "//div[contains(text(),'중지중으로 이동')]")
    delete_icon = (By.XPATH, "//div[contains(text(),'삭제')]")
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
    selectBtn = (By.XPATH, "//button[contains(text(),'선택')]")

    # 추가
    addBtn = (By.XPATH, "//button[contains(text(),'추가')]")
    a_type = (By.XPATH, "//button[contains(text(),'A안')]")
    b_type = (By.XPATH, "//button[contains(text(),'B안')]")
    c_type = (By.XPATH, "//button[contains(text(),'C안')]")
    d_type = (By.XPATH, "//button[contains(text(),'D안')]")
    e_type = (By.XPATH, "//button[contains(text(),'E안')]")
    type_del_icon = (By.XPATH, "(//button[@type='button'])[11]")

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

    # A/B/N 테스트 설정
    type_auto = (By.XPATH, "//input[@value='true']")
    target_order = (By.XPATH, "//input[@value='OR']")

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

    # -------------------------동작 선언 영역-------------------------
    # AI 상품 추천 캠페인 메뉴
    def click_campaign_menu(self):
        return self.driver.find_element(*CampaignPage.campaignMenu)

    # 만들기
    def click_create_btn(self):
        return self.driver.find_element(*CampaignPage.createBtn)

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

    # 삭제할 캠페인 찾기
    @staticmethod
    def click_tools_icon_by_name(cam_element, driver):
        # row 찾기
        row = cam_element.find_element(By.XPATH, "./ancestor::div[contains(@class,'MuiDataGrid-row')]")

        # row index 저장
        row_index = row.get_attribute("data-rowindex")

        # 버튼 찾기
        pinned_container = driver.find_element(By.XPATH, "//div[contains(@class,'MuiDataGrid-pinnedColumns--right')]")
        buttons = pinned_container.find_elements(By.XPATH, ".//button[contains(@class,'MuiIconButton-root')]")

        # 버튼과 row index 매칭
        target_btn = None
        for btn in buttons:
            btn_row = btn.find_element(By.XPATH, "./ancestor::div[contains(@class,'MuiDataGrid-row')]")
            btn_row_index = btn_row.get_attribute("data-rowindex")
            if btn_row_index == row_index:
                target_btn = btn
                break

        return target_btn

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
        return self.driver.find_element(*CampaignPage.now_pc_seg)
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

    # A/B/N 테스트 설정
    def click_type_auto(self):
        return self.driver.find_element(*CampaignPage.type_auto)
    def click_target_order(self):
        return self.driver.find_element(*CampaignPage.target_order)

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
        return self.driver.find_element(*CampaignPage.cam_popup)