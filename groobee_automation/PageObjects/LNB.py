from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Dashboard:

    def __init__(self, driver):
        self.driver = driver

    #-------------------------element 선언 영역-------------------------
    #애널리틱스
    dashboardMenu = (By.XPATH, "//p[contains(text(),'대시보드')]")
    monitoringMenu = (By.XPATH, "//p[contains(text(),'실시간')]")
    dataMonitoringMenu = (By.XPATH, "//p[contains(text(),'데이터 모니터링')]")
    #세그먼트
    aisegmentMenu = (By.XPATH, "//p[contains(text(),'AI 세그먼트 타겟팅')]")
    segmentMenu = (By.XPATH, "//p[contains(text(),'세그먼트 타겟팅')]")
    #온사이트
    recommendMenu = (By.XPATH, "//p[contains(text(),'AI 상품 추천 캠페인')]")
    campaignMenu = (By.XPATH, "//p[contains(text(),'온사이트 캠페인')]")
    #오프사이트
    pushNotiMenu = (By.XPATH, "//p[contains(text(),'푸시 알림 캠페인')]")
    kakaoMomentMenu = (By.XPATH, "//p[contains(text(),'카카오톡 캠페인: 모먼트')]")
    kakaoAlimMenu = (By.XPATH, "//p[contains(text(),'카카오톡 캠페인: 알림톡')]")
    #LNB>관리
    settingMenu = (By.XPATH, "//p[contains(text(),'설정')]")
    helpMenu = (By.XPATH, "//p[contains(text(),'도움말')]")

    #-------------------------동작 선언 영역-------------------------
    #애널리틱스
    def click_dashboard_menu(self):
        self.driver.find_element(*Dashboard.dashboardMenu).click()
    def click_monitoring_menu(self):
        self.driver.find_element(*Dashboard.monitoringMenu).click()
    def click_datamonitoring_menu(self):
        self.driver.find_element(*Dashboard.dataMonitoringMenu).click()
    #세그먼트
    def click_aisegment_menu(self):
        self.driver.find_element(*Dashboard.aisegmentMenu).click()
    def click_segment_menu(self):
        self.driver.find_element(*Dashboard.segmentMenu).click()
    #온사이트
    def click_recommend_menu(self):
        self.driver.find_element(*Dashboard.recommendMenu).click()
    def click_campaign_menu(self):
        self.driver.find_element(*Dashboard.campaignMenu).click()
    #오프사이트
    def click_pushnoti_menu(self):
        self.driver.find_element(*Dashboard.pushNotiMenu).click()
    def click_kakaomoment_menu(self):
        self.driver.find_element(*Dashboard.kakaoMomentMenu).click()
    def click_kakaoalim_menu(self):
        self.driver.find_element(*Dashboard.kakaoAlimMenu).click()
    #관리
    def click_setting_menu(self):
        self.driver.find_element(*Dashboard.settingMenu).click()
    def click_help_menu(self):
        self.driver.find_element(*Dashboard.helpMenu).click()