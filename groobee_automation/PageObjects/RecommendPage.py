from selenium.webdriver.common.by import By

class RecommendPage:

    def __init__(self, driver):
        self.driver = driver

    # -------------------------element 선언 영역-------------------------
    # AI 상품 추천 캠페인 메뉴
    recommendMenu = (By.XPATH, "//p[contains(text(),'AI 상품 추천 캠페인')]")

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
    code_copy_icon = (By.XPATH, "//div[contains(text(),'코드 복사')]")
    moveto_storage = (By.XPATH, "//div[contains(text(),'보관함으로 이동')]")
    moveto_pause = (By.XPATH, "//div[contains(text(),'중지중으로 이동')]")
    delete_icon = (By.XPATH, "//div[contains(text(),'삭제')]")
    delete_icon_cancel = (By.XPATH, "//button[contains(text(),'취소')]")
    delete_icon_confirm = (By.XPATH, "//button[contains(text(),'확인')]")

    # 캠페인 입력
    cam_title = (By.XPATH, "//h1[contains(text(),'새로운 AI 상품 추천 캠페인 만들기')]")
    cam_name = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 40자']")
    cam_des = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 400자']")

    # 접속 유형
    type_pcweb = (By.XPATH, "//input[@value='PC']")
    type_mobile = (By.XPATH, "//input[@value='MO']")
    type_mobile_web = (By.XPATH, "//input[@value='MW']")
    type_mobile_app = (By.XPATH, "//input[@value='MA']")

    # 알고리즘 설정
    set_algo_goods = (By.XPATH, "//input[@value='GD']")
    set_algo_special = (By.XPATH, "//input[@value='PL']")
    goods_all_cb = (By.XPATH, "(//input[@type='checkbox'])[1]")
    visitors_all_cb = (By.XPATH, "(//input[@type='checkbox'])[11]")
    stat_all_cb = (By.XPATH, "(//input[@type='checkbox'])[18]")

    # 최적화 목표
    target_click = (By.XPATH, "//input[@value='CL']")
    target_order = (By.XPATH, "//input[@value='OR']")

    # 타겟 설정
    target_set = (By.XPATH, "//h6[contains(text(),'타겟 설정')]")
    seg_load = (By.XPATH, "//button[contains(text(),'세그먼트 불러오기')]")

    # 세그먼트 불러오기 RNB(설정할 값 실제 작성)
    aiseg_tab = (By.XPATH, "//button[@id='basic-tab-0']")
    seg_tab = (By.XPATH, "//button[@id='basic-tab-1']")
    purchase_self_seg = (By.XPATH, "//h6[contains(text(),'[QA] 직접 입력 테스트 세그먼트')]")
    selectBtn = (By.XPATH, "//button[contains(text(),'선택')]")

    # 디자인 유형
    design_script = (By.XPATH, "//input[@value='JS']")
    design_data = (By.XPATH, "//input[@value='CU']")

    # 필터링 설정
    filter_click = (By.XPATH, "(//input[@type='checkbox'])[1]")
    filter_order = (By.XPATH, "(//input[@type='checkbox'])[2]")

    # 스케줄
    schedule_self = (By.XPATH, "//input[@value='MA']")
    schedule_enter = (By.XPATH, "//input[@value='ET']")

    # 완료
    cancelBtn = (By.XPATH, "//button[contains(text(),'취소')]")
    nextBtn = (By.XPATH, "//button[contains(text(),'다음 단계')]")
    saveBtn = (By.XPATH, "//button[contains(text(),'저장')]")

    # -------------------------동작 선언 영역-------------------------
    # AI 상품 추천 캠페인 메뉴
    def click_recommend_menu(self):
        return self.driver.find_element(*RecommendPage.recommendMenu)

    # 만들기
    def click_create_btn(self):
        return self.driver.find_element(*RecommendPage.createBtn)

    # 상태탭
    def click_progress_tab(self):
        return self.driver.find_element(*RecommendPage.progress_tab)
    def click_pause_tab(self):
        return self.driver.find_element(*RecommendPage.pause_tab)
    def click_storage_tab(self):
        return self.driver.find_element(*RecommendPage.storage_tab)

    # 상태
    def click_status_icon_play(self):
        return self.driver.find_element(*RecommendPage.status_icon_play)
    def click_status_icon_pause(self):
        return self.driver.find_element(*RecommendPage.status_icon_pause)
    def click_status_icon_cancel(self):
        return self.driver.find_element(*RecommendPage.status_icon_cancel)
    def click_status_icon_confirm(self):
        return self.driver.find_element(*RecommendPage.status_icon_confirm)

    # 관리 도구
    def click_tools_icon(self):
        return self.driver.find_element(*RecommendPage.tools_icon)
    def click_update_icon(self):
        return self.driver.find_element(*RecommendPage.update_icon)
    def click_copy_icon(self):
        return self.driver.find_element(*RecommendPage.copy_icon)
    def click_report_icon(self):
        return self.driver.find_element(*RecommendPage.report_icon)
    def click_view_icon(self):
        return self.driver.find_element(*RecommendPage.view_icon)
    def click_code_copy_icon(self):
        return self.driver.find_element(*RecommendPage.code_copy_icon)
    def click_moveto_storage_icon(self):
        return self.driver.find_element(*RecommendPage.moveto_storage)
    def click_moveto_pause_icon(self):
        return self.driver.find_element(*RecommendPage.moveto_pause)
    def click_delete_icon(self):
        return self.driver.find_element(*RecommendPage.delete_icon)
    def click_delete_icon_cancel(self):
        return self.driver.find_element(*RecommendPage.delete_icon_cancel)
    def click_delete_icon_confirm(self):
        return self.driver.find_element(*RecommendPage.delete_icon_confirm)

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
        return self.driver.find_element(*RecommendPage.cam_name)
    def send_cam_des(self):
        return self.driver.find_element(*RecommendPage.cam_des)

    # 접속 유형
    def click_type_pcweb(self):
        return self.driver.find_element(*RecommendPage.type_pcweb)
    def click_type_mobile(self):
        return self.driver.find_element(*RecommendPage.type_mobile)
    def click_type_mobile_web(self):
        return self.driver.find_element(*RecommendPage.type_mobile_web)
    def click_type_mobile_app(self):
        return self.driver.find_element(*RecommendPage.type_mobile_app)

   # 알고리즘 설정
    def click_set_algo_goods(self):
        return self.driver.find_element(*RecommendPage.set_algo_goods)
    def click_set_algo_special(self):
        return self.driver.find_element(*RecommendPage.set_algo_special)
    def click_goods_all_cb(self):
        return self.driver.find_element(*RecommendPage.goods_all_cb)
    def click_visitors_all_cb(self):
        return self.driver.find_element(*RecommendPage.visitors_all_cb)
    def click_stat_all_cb(self):
        return self.driver.find_element(*RecommendPage.stat_all_cb)

    # 최적화 목표
    def click_target_click(self):
        return self.driver.find_element(*RecommendPage.target_click)
    def click_target_order(self):
        return self.driver.find_element(*RecommendPage.target_order)

    # 타겟 설정
    def click_target_set(self):
        return self.driver.find_element(*RecommendPage.target_set)
    def click_seg_load(self):
        return self.driver.find_element(*RecommendPage.seg_load)

    # 세그먼트 불러오기 RNB(설정할 값 실제 작성)
    def click_aiseg_tab(self):
        return self.driver.find_element(*RecommendPage.aiseg_tab)
    def click_seg_tab(self):
        return self.driver.find_element(*RecommendPage.seg_tab)
    def click_purchase_self_seg(self):
        return self.driver.find_element(*RecommendPage.purchase_self_seg)
    def click_select_btn(self):
        return self.driver.find_element(*RecommendPage.selectBtn)

    # 디자인 유형
    def click_design_script(self):
        return self.driver.find_element(*RecommendPage.design_script)
    def click_design_data(self):
        return self.driver.find_element(*RecommendPage.design_data)

    # 필터링 설정
    def click_filter_click(self):
        return self.driver.find_element(*RecommendPage.filter_click)
    def click_filter_order(self):
        return self.driver.find_element(*RecommendPage.filter_order)

    # 스케줄
    def click_schedule_self(self):
        return self.driver.find_element(*RecommendPage.schedule_self)
    def click_schedule_enter(self):
        return self.driver.find_element(*RecommendPage.schedule_enter)

    # 완료
    def click_cancel_btn(self):
        return self.driver.find_element(*RecommendPage.cancelBtn)
    def click_next_btn(self):
        return self.driver.find_element(*RecommendPage.nextBtn)
    def click_save_btn(self):
        return self.driver.find_element(*RecommendPage.saveBtn)

    # 생성된 캠페인 리스트
    def get_cam_list_item(self, cam_name):
        return self.driver.find_element(By.XPATH, f"//p[contains(text(), '{cam_name}')]")