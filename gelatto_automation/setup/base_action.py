
from selenium.common.exceptions import TimeoutException

from setup.selenium_utils import safe_find, safe_click, clear_input
from setup.logger import info, warn, error

class BaseAction:

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    # Wrapper for find
    def find(self, locator, name="element"):
        elem = safe_find(self.driver, locator, name)
        return elem

    # Wrapper for click
    def click(self, locator, name="element"):
        result = safe_click(self.driver, locator, name)
        if result:
            info(f"[Action] Clicked {name}")
        else:
            warn(f"[Action] Click failed for {name}")
        return result

    # Wrapper for text input
    def input(self, locator, text, name="input field"):
        elem = safe_find(self.driver, locator, name)
        if elem:
            status = clear_input(elem, name)
            elem.send_keys(text)
            info(f"[Action] Typed into {name}: {text}")
            return True

        warn(f"[Action] Cannot input — {name} not found")
        return False

    # Optional: Wait and click
    def wait_and_click(self, condition, locator, name="element"):
        info(name)
        try:
            self.wait.until(condition(locator))
            return self.click(locator, name)
        except TimeoutException:
            warn(f"[Action] Timeout waiting for {name}")
            return False
        except Exception as e:
            error(f"[Action] Unexpected error waiting for {name}: {e}")
            return False
        