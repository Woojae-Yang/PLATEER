import pytest
import inspect
import logging

from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webdriver import WebDriver

@pytest.mark.usefixtures("setup")
class BaseClass:
    driver: WebDriver = None

    #옵션 선택 유틸 함수
    @staticmethod
    def select_options(locator, text):
        sel = Select(locator)
        sel.select_by_visible_text(text)

    #로그 유틸 함수
    @staticmethod
    def get_log():
        log_name = inspect.stack()[1][3]
        log = logging.getLogger(log_name)

        if not log.handlers:
            file_handler = logging.FileHandler(r"/Users/ywj/Documents/PLATEER/automation/log/logfile.log", encoding="utf-8")
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            log.addHandler(file_handler)
            log.setLevel(logging.DEBUG)

        return log