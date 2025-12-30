
import platform 
import traceback
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException, 
    ElementClickInterceptedException, 
    TimeoutException)
from setup.logger import info, warn, error, debug

## 운영체제에 따른 텍스트박스 전체 삭제 처리
def clear_input(elem, name = "input field"):
    """입력창 전체 삭제 + 로깅"""
    system = platform.system().lower()
    modifier = Keys.COMMAND if "darwin" in system else Keys.CONTROL

    try:
        elem.click()
        elem.send_keys(modifier, "a")
        time.sleep(2)
        elem.send_keys(Keys.DELETE)
        time.sleep(2)
        info(f"[clear_input] Cleared text in {name}")
        return True
    except Exception as e:
        error(f"[clear_input] Failed to clear {name}: {e}")
        debug(traceback.format_exc())
        return False
    

def safe_find(driver, locator, name="element"):
    """요소 찾기 (없으면 None + 로깅)"""

    try:
        elem = driver.find_element(*locator)
        info(f"[safe_find] Found {name}")
        return elem

    except NoSuchElementException:
        warn(f"[safe_find] {name} not found")
        return None

    except Exception as e:
        error(f"[safe_find] Unexpected error for {name}: {e}")
        debug(traceback.format_exc())
        return None



def safe_click(driver, locator, name="element"):
    """요소 클릭 (실패해도 예외 없이 로그만 남김)"""

    try:
        elem = driver.find_element(*locator)
        elem.click()
        info(f"[safe_click] Clicked {name}")
        return True

    except NoSuchElementException:
        warn(f"[safe_click] {name} not found — skip")
        return False

    except ElementClickInterceptedException:
        warn(f"[safe_click] {name} was intercepted — skip")
        return False

    except Exception as e:
        error(f"[safe_click] Unexpected error clicking {name}: {e}")
        debug(traceback.format_exc())
        return False


def wait_new_tab(driver, before_handles, timeout=10):
    WebDriverWait(driver, timeout).until(lambda d: len(d.window_handles) > len(before_handles))
    after = set(driver.window_handles)
    new_handle = list(after - set(before_handles))[0]
    return new_handle


'''
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

'''