import os
import inspect
import logging
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException, WebDriverException


class BaseClass:
    driver: WebDriver = None

    # 옵션 선택 유틸 함수
    @staticmethod
    def select_options(locator, text):
        sel = Select(locator)
        sel.select_by_visible_text(text)

    # 웹 요소 대기 유틸 함수(노출)
    @staticmethod
    def wait_visible(driver, locator, timeout=10):
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    # 오버레이 대기 함수
    OVERLAY = (By.CSS_SELECTOR, ".MuiBackdrop-root, .MuiModal-backdrop")
    @staticmethod
    def wait_overlay_gone(driver, timeout=5):
        WebDriverWait(driver, timeout, poll_frequency=0.05).until(
            lambda d: all(not el.is_displayed() for el in d.find_elements(*BaseClass.OVERLAY))
        )

    # 웹 요소 대기 유틸 함수(클릭)
    @staticmethod
    def wait_clickable(driver, locator, timeout=10):
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )

    # 프로젝트 루트 경로 찾기
    @staticmethod
    def project_root() -> str:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # 파일 전달
    @staticmethod
    def getdata_file(filename: str) -> str:
        return os.path.join(BaseClass.project_root(), "TestData", filename)

    # 리프레시 안정화 유틸 함수
    @staticmethod
    def refresh_page(driver, wait_locator=None, timeout=10, retry=1):
        log = BaseClass.get_log()
        for attempt in range(retry + 1):
            try:
                log.info(f"페이지 새로고침 시도 ({attempt + 1}/{retry + 1})")
                driver.refresh()

                # Document Ready 상태 확인
                WebDriverWait(driver, timeout).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )

                # 특정 요소가 있다면 그 요소까지 보장
                if wait_locator:
                    BaseClass.wait_visible(driver, wait_locator, timeout)

                log.info("페이지 리프레시 완료")
                return True

            except (TimeoutException, WebDriverException):
                log.warning("Refresh 이후 페이지 안정화 실패, 재시도 중...")
                time.sleep(1)

        log.error("Refresh 실패! 페이지가 완전히 로드되지 않았습니다.")
        return False

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