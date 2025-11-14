from selenium.webdriver.common.by import By

class AisegmentPage:

    def __init__(self, driver):
        self.driver = driver

    # -------------------------element 선언 영역-------------------------
    # AI 세그먼트 타겟팅 메뉴
    aisegmentMenu = (By.XPATH, "//p[contains(text(),'AI 세그먼트 타겟팅')]")

    # 만들기 진입
    createBtn = (By.XPATH, "//button[contains(text(),'만들기')]")
    rfm_seg = (By.XPATH, "//li[contains(text(),'RFM 세그먼트')]")
    purchase_seg = (By.XPATH, "//li[contains(text(),'구매 확률 세그먼트')]")
    tastes_seg = (By.XPATH, "//li[contains(text(),'취향 분석 세그먼트')]")

    # RFM 세그먼트
    rfm_seg_title = (By.XPATH, "//h1[contains(text(),'새로운 RFM 세그먼트 만들기')]")
    rfm_seg_name = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 40자']")
    rfm_seg_des = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 400자']")

    # RFM 선택
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

    # 완료
    cancelBtn = (By.XPATH, "//button[contains(text(),'취소')]")
    saveBtn = (By.XPATH, "//button[contains(text(),'저장')]")

    # -------------------------동작 선언 영역-------------------------
    # AI 세그먼트 타겟팅 메뉴
    def click_aisegment_menu(self):
        return self.driver.find_element(*AisegmentPage.aisegmentMenu)

    # 만들기 진입
    def click_create_btn(self):
        return self.driver.find_element(*AisegmentPage.createBtn)
    def click_rfm_seg(self):
        return self.driver.find_element(*AisegmentPage.rfm_seg)
    def click_purchase_seg(self):
        return self.driver.find_element(*AisegmentPage.purchase_seg)
    def click_tastes_seg(self):
        return self.driver.find_element(*AisegmentPage.tastes_seg)

    # RFM 세그먼트 입력
    def send_rfm_seg_name(self):
        return self.driver.find_element(*AisegmentPage.rfm_seg_name)
    def send_rfm_seg_des(self):
        return self.driver.find_element(*AisegmentPage.rfm_seg_des)

    # RFM 선택 옵션을 dict 형태로 반환
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

    # 완료
    def click_cancel_btn(self):
        return self.driver.find_element(*AisegmentPage.cancelBtn)
    def click_save_btn(self):
        return self.driver.find_element(*AisegmentPage.saveBtn)

    # 생성된 세그먼트 리스트
    def get_seg_list_item(self, seg_name):
        return self.driver.find_element(By.XPATH, f"//p[contains(text(), '{seg_name}')]")