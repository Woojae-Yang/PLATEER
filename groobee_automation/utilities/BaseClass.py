import os
import inspect
import logging

from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webdriver import WebDriver

class BaseClass:
    driver: WebDriver = None

    # 옵션 선택 유틸 함수
    @staticmethod
    def select_options(locator, text):
        sel = Select(locator)
        sel.select_by_visible_text(text)

    # 로그 유틸 함수
    @staticmethod
    def get_log():
        log_name = inspect.stack()[1][3]
        log = logging.getLogger(log_name)

        if not log.handlers:
            current_file = os.path.abspath(__file__)
            project_dir = os.path.dirname(os.path.dirname(current_file))
            log_dir = os.path.join(project_dir, "reports")
            os.makedirs(log_dir, exist_ok=True)
            log_file_path = os.path.join(log_dir, "logfile.log")
            file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
            file_handler.setFormatter(formatter)
            log.addHandler(file_handler)
            log.setLevel(logging.DEBUG)

        return log