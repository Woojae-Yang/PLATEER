import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager # Chrome driver 자동 업데이트
from webdriver_manager.microsoft import EdgeChromiumDriverManager # Edge driver 자동 업데이트

# 브라우저 선택 옵션
def pytest_addoption(parser):
    parser.addoption("--browser_name", action="store", default="chrome")
    parser.addoption("--url", action="store", default="https://admin.groobee.io/login")

@pytest.fixture(scope="session")
def driver(request):
    browser_name = request.config.getoption("--browser_name")
    target_url = request.config.getoption("--url")

    # 브라우저 실행
    if browser_name.lower() == "chrome":
        service_obj = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service_obj)
    elif browser_name.lower() == "edge":
        service_obj = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service_obj)
    else:
        raise ValueError(f"지원하지 않는 브라우저: {browser_name}")

    driver.get(target_url)
    driver.implicitly_wait(5)
    driver.maximize_window()

    yield driver

    driver.quit()