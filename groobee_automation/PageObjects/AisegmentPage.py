from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class AisegmentPage:

    def __init__(self, driver):
        self.driver = driver

    # -------------------------element 선언 영역-------------------------
    # AI 세그먼트 타겟팅 메뉴
    aisegmentMenu = (By.XPATH, "//a[@href='/aisegment']")

    # 만들기
    createBtn = (By.XPATH, "//button[contains(text(),'만들기')]")
    rfm_seg = (By.XPATH, "//li[contains(text(),'RFM 세그먼트')]")
    purchase_seg = (By.XPATH, "//li[contains(text(),'구매 확률 세그먼트')]")
    tastes_seg = (By.XPATH, "//li[contains(text(),'취향 분석 세그먼트')]")

    # 관리 도구
    tools_icon = (By.XPATH, "//div[@class='MuiDataGrid-row']//button[@type='button']")
    update_icon = (By.XPATH, "//p[contains(text(),'수정')]")
    copy_icon = (By.XPATH, "//p[contains(text(),'복사')]")
    delete_icon = (By.XPATH, "//p[contains(text(),'삭제')]")
    delete_icon_cancel = (By.XPATH, "//button[contains(text(),'취소')]")
    delete_icon_confirm = (By.XPATH, "//button[contains(text(),'확인')]")

    # RFM 세그먼트
    rfm_seg_title = (By.XPATH, "//h1[contains(text(),'새로운 RFM 세그먼트 만들기')]")
    rfm_seg_name = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 40자']")
    rfm_seg_des = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 400자']")

    # RFM 세그먼트 선택
    seg_vip = (By.XPATH, "//h6[normalize-space()='VIP']")
    seg_rare = (By.XPATH, "//h6[contains(text(),'뜸한 VIP')]")
    seg_poten = (By.XPATH, "//h6[contains(text(),'잠재 VIP')]")
    seg_new = (By.XPATH, "//h6[contains(text(),'신규 고객')]")
    seg_now = (By.XPATH, "//h6[contains(text(),'지금 잡아야 할 고객')]")
    seg_care = (By.XPATH, "//h6[contains(text(),'신경써야 할 고객')]")
    seg_worry = (By.XPATH, "//h6[contains(text(),'이탈 우려')]")
    seg_left_vip = (By.XPATH, "//h6[contains(text(),'이탈한 VIP')]")
    seg_left_poten_vip = (By.XPATH, "//h6[contains(text(),'이탈한 잠재 VIP')]")
    seg_left = (By.XPATH, "//h6[contains(text(),'이탈한 고객')]")

    # 구매 확률 세그먼트
    purchase_seg_title = (By.XPATH, "//h1[contains(text(),'새로운 구매 확률 세그먼트 만들기')]")
    purchase_seg_name = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 40자']")
    purchase_seg_des = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 400자']")

    # 구매 확률 세그먼트 선택
    purchase_combo = (By.XPATH, "//div[@role='combobox']")
    purchase_20 = (By.XPATH, "//li[normalize-space()='0~20%']")
    purchase_40 = (By.XPATH, "//li[normalize-space()='21~40%']")
    purchase_60 = (By.XPATH, "//li[normalize-space()='41~60%']")
    purchase_80 = (By.XPATH, "//li[normalize-space()='61~80%']")
    purchase_100 = (By.XPATH, "//li[normalize-space()='81~100%']")
    purchase_self = (By.XPATH, "//li[contains(text(),'직접 입력')]")
    purchase_min = (By.XPATH, "//div[contains(@class,'MuiStack-root')]//input[@type='text'][1]")
    purchase_max = (By.XPATH, "//div[contains(@class,'MuiStack-root')]//input[@type='text'][2]")
    checkBtn = (By.XPATH, "//button[contains(text(),'확인하기')]")

    # 취향 분석 세그먼트
    tastes_seg_title = (By.XPATH, "//h1[contains(text(),'새로운 취향 분석 세그먼트 만들기')]")
    tastes_seg_name = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 40자']")
    tastes_seg_des = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 400자']")

    # 취향 분석 세그먼트 선택
    tastes_seg_main = (By.XPATH, "//button[contains(text(),'대표 상품')]")
    tastes_seg_view = (By.XPATH, "//button[contains(text(),'많이 조회한 상품')]")
    tastes_handmade = (By.XPATH, "//h6[contains(text(),'핸드메이드 코트 선호')]")

    # 완료
    cancelBtn = (By.XPATH, "//button[contains(text(),'취소')]")
    saveBtn = (By.XPATH, "//button[contains(text(),'저장')]")

    # -------------------------동작 선언 영역-------------------------
    # AI 세그먼트 타겟팅 메뉴
    def click_aisegment_menu(self):
        return self.driver.find_element(*AisegmentPage.aisegmentMenu)

    # 만들기
    def click_create_btn(self):
        return self.driver.find_element(*AisegmentPage.createBtn)
    def click_rfm_seg(self):
        return self.driver.find_element(*AisegmentPage.rfm_seg)
    def click_purchase_seg(self):
        return self.driver.find_element(*AisegmentPage.purchase_seg)
    def click_tastes_seg(self):
        return self.driver.find_element(*AisegmentPage.tastes_seg)

    # 관리 도구
    def click_tools_icon(self):
        return self.driver.find_element(*AisegmentPage.tools_icon)
    def click_update_icon(self):
        return self.driver.find_element(*AisegmentPage.update_icon)
    def click_copy_icon(self):
        return self.driver.find_element(*AisegmentPage.copy_icon)
    def click_delete_icon(self):
        return self.driver.find_element(*AisegmentPage.delete_icon)
    def click_delete_icon_cancel(self):
        return self.driver.find_element(*AisegmentPage.delete_icon_cancel)
    def click_delete_icon_confirm(self):
        return self.driver.find_element(*AisegmentPage.delete_icon_confirm)

    # 삭제할 세그먼트 찾기
    @staticmethod
    def click_tools_icon_by_name(seg_element, driver):
        # row 찾기
        row = seg_element.find_element(By.XPATH, "./ancestor::div[contains(@class,'MuiDataGrid-row')]")

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

    # RFM 세그먼트 입력
    def send_rfm_seg_name(self):
        return self.driver.find_element(*AisegmentPage.rfm_seg_name)
    def send_rfm_seg_des(self):
        return self.driver.find_element(*AisegmentPage.rfm_seg_des)

    # RFM 세그먼트 선택 옵션을 dict 형태로 반환
    def get_rfm_options(self):
        return {
            "VIP": self.driver.find_element(*AisegmentPage.seg_vip),
            "뜸한 VIP": self.driver.find_element(*AisegmentPage.seg_rare),
            "잠재 VIP": self.driver.find_element(*AisegmentPage.seg_poten),
            "신규 고객": self.driver.find_element(*AisegmentPage.seg_new),
            "지금 잡아야 할 고객": self.driver.find_element(*AisegmentPage.seg_now),
            "신경써야 할 고객": self.driver.find_element(*AisegmentPage.seg_care),
            "이탈 우려": self.driver.find_element(*AisegmentPage.seg_worry),
            "이탈한 VIP": self.driver.find_element(*AisegmentPage.seg_left_vip),
            "이탈한 잠재 VIP": self.driver.find_element(*AisegmentPage.seg_left_poten_vip),
            "이탈한 고객": self.driver.find_element(*AisegmentPage.seg_left),
        }

    # 구매 확률 세그먼트 입력
    def send_purchase_seg_name(self):
        return self.driver.find_element(*AisegmentPage.purchase_seg_name)
    def send_purchase_seg_des(self):
        return self.driver.find_element(*AisegmentPage.purchase_seg_des)
    def send_purchase_seg_min(self):
        return WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(AisegmentPage.purchase_min)
        )
    def send_purchase_seg_max(self):
        return WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(AisegmentPage.purchase_max)
        )
    def click_check_btn(self):
        return self.driver.find_element(*AisegmentPage.checkBtn)

    # 구매 확률 세그먼트 선택
    def click_purchase_combo(self):
        return self.driver.find_element(*AisegmentPage.purchase_combo)

    # 구매 확률 세그먼트 선택 옵션을 dict 형태로 반환
    def get_purchase_options(self):
        self.click_purchase_combo().click()

        WebDriverWait(self.driver, 5).until(
            EC.visibility_of_element_located(AisegmentPage.purchase_20)
        )

        options = {
            "0~20%": self.driver.find_element(*AisegmentPage.purchase_20),
            "21~40%": self.driver.find_element(*AisegmentPage.purchase_40),
            "41~60%": self.driver.find_element(*AisegmentPage.purchase_60),
            "61~80%": self.driver.find_element(*AisegmentPage.purchase_80),
            "81~100%": self.driver.find_element(*AisegmentPage.purchase_100),
            "직접 입력": self.driver.find_element(*AisegmentPage.purchase_self),
        }

        # 스크롤 후 읽기
        for opt in options.values():
            self.driver.execute_script("arguments[0].scrollIntoView(true);", opt)

        # 콤보 박스 닫기
        self.driver.find_element(*AisegmentPage.purchase_20).click()
        return options

    # 취향 분석 세그먼트 입력
    def send_tastes_seg_name(self):
        return self.driver.find_element(*AisegmentPage.tastes_seg_name)
    def send_tastes_seg_des(self):
        return self.driver.find_element(*AisegmentPage.tastes_seg_des)

    # 취향 분석 세그먼트 선택
    def click_tastes_seg_main(self):
        return self.driver.find_element(*AisegmentPage.tastes_seg_main)
    def click_tastes_seg_view(self):
        return self.driver.find_element(*AisegmentPage.tastes_seg_view)
    def click_tastes_handmade(self):
        return self.driver.find_element(*AisegmentPage.tastes_handmade)

    # 완료
    def click_cancel_btn(self):
        return self.driver.find_element(*AisegmentPage.cancelBtn)
    def click_save_btn(self):
        return self.driver.find_element(*AisegmentPage.saveBtn)

    # 생성된 세그먼트 리스트
    def get_seg_list_item(self, seg_name):
        return self.driver.find_element(By.XPATH, f"//p[contains(text(), '{seg_name}')]")