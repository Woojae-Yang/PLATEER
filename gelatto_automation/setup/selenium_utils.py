
import platform 
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException


## 운영체제에 따른 텍스트박스 전체 삭제 처리
def clear_input(elem):
    """운영체제에 맞게 텍스트 전체 삭제"""

    system = platform.system().lower()
    modifier = Keys.COMMAND if "darwin" in system else Keys.CONTROL

    elem.click()
    elem.send_keys(modifier, "a")
    elem.send_keys(Keys.DELETE)


## 특정 요소가 없으면 그냥 NONE 반환하고 스킵
def safe_find(driver, locator):
    try:
        return driver.find_element(*locator)
    except NoSuchElementException:
        return None


## 특정 요소가 있으면 클릭, 없으면 그냥 스킵
def safe_click(driver, locator):
    try:
        elem = driver.find_element(*locator)
        elem.click()
        return True
    except (NoSuchElementException, ElementClickInterceptedException):
        return False