import time
import pytest

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PageObjects.LoginPage import LoginPage
from TestData.LoginData import LoginData
from utilities.BaseClass import BaseClass

# 엑셀 데이터 불러오기
@pytest.fixture(params=LoginData.get_excel_data("1"))
def get_data(request):
    return request.param

class TestLogin(BaseClass):

    login_expect_title = "대시보드 :: GROOBEE"

    def test_login(self, driver, get_data):
        log = self.get_log()

        groobee = LoginPage(driver)

        # ID/PW 입력
        groobee.send_id().send_keys(get_data["ID"])
        groobee.send_pw().send_keys(get_data["PW"])
        time.sleep(1)

        # 로그인 시도
        groobee.click_login_btn().click()
        
        # 고객사 검색
        groobee.search_shop().send_keys("groobeeshop")
        time.sleep(1)

        # 그루비샵 선택
        groobee.click_shop_login_btn().click()

        # 대시보드 메뉴 노출까지 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(LoginPage.dashboardMenu)
        )

        # 대시보드 진입 확인
        assert driver.title == self.login_expect_title
        log.info(driver.title)