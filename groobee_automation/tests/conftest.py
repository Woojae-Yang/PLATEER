import os
import pytest
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

from PageObjects.LoginPage import LoginPage


# ==========================
# Env load
# ==========================
def _load_env():
    # 기본적으로 프로젝트 루트의 ".env"를 로드
    load_dotenv()


_load_env()


# ==========================
# Pytest CLI options
# ==========================
def pytest_addoption(parser):
    # 브라우저는 일단 chrome만 사용 (docker 기준)
    parser.addoption("--browser_name", action="store", default="chrome")
    parser.addoption("--headless", action="store", default="false")

    # TestRail 연동 옵션
    parser.addoption("--testrail-run-id", action="store", default=None)
    parser.addoption("--testrail-upload", action="store", default="true")  # true/false


# ==========================
# Fixtures
# ==========================
@pytest.fixture(scope="session")
def testrail_run_id(request):
    cli = request.config.getoption("--testrail-run-id")
    if cli:
        return int(cli)

    env = os.getenv("TESTRAIL_RUN_ID")
    return int(env) if env else None


@pytest.fixture(scope="session")
def driver(request):
    # Docker 환경 여부 판단
    in_docker = os.path.exists("/.dockerenv")

    # headless 여부 결정
    cli_headless = request.config.getoption("--headless").lower() == "true"
    headless_enabled = in_docker or cli_headless  # Docker에서는 기본 headless

    # Chrome 옵션 설정
    options = ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=ko-KR")
    options.add_argument("--accept-lang=ko-KR")
    options.add_argument("Accept-Language=ko-KR")
    if headless_enabled:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")

    # 드라이버 경로 설정
    if in_docker:
        driver_path = "/usr/local/bin/chromedriver"
        service = Service(driver_path)
    else:
        from webdriver_manager.chrome import ChromeDriverManager

        driver_path = ChromeDriverManager().install()

        # Chrome for Testing 구조 때문에 잘못된 파일명을 잡는 케이스 방지
        if driver_path.endswith("THIRD_PARTY_NOTICES.chromedriver"):
            driver_path = driver_path.replace("THIRD_PARTY_NOTICES.chromedriver", "chromedriver")

        service = Service(driver_path)

    # 드라이버 생성 (여기서는 브라우저만 띄움)
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(5)

    # 로컬(비 headless)일 때만 maximize
    if not headless_enabled:
        driver.maximize_window()

    yield driver
    driver.quit()


@pytest.fixture
def login(driver):
    base_url = os.getenv("GROOBEE_BASE_URL")
    user_id = os.getenv("GROOBEE_ID")
    user_pw = os.getenv("GROOBEE_PW")
    shop = os.getenv("GROOBEE_SHOP")

    assert base_url, "GROOBEE_BASE_URL not set"
    assert user_id, "GROOBEE_ID not set"
    assert user_pw, "GROOBEE_PW not set"
    assert shop, "GROOBEE_SHOP not set"

    driver.get(base_url)

    groobee = LoginPage(driver)

    # ID/PW 입력 > 로그인 버튼 선택
    groobee.send_id(user_id)
    groobee.send_pw(user_pw)
    groobee.click_login()

    # 전체 통합 검색 필드 > shop 검색
    groobee.search_shop(shop)

    # 고객사 로그인
    groobee.click_shop_login()

    # 대시보드 로드 확인
    assert groobee.wait_dashboard_loaded(), "Dashboard not loaded"

    return groobee

@pytest.fixture
def clear_campaigns():
    def _clear(page_obj, timeout=10):
        page_obj.move_all_running_to_pause(timeout=timeout)
    return _clear


# ==========================
# Hooks
# ==========================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    driver = item.funcargs.get("driver", None)

    # 실패 시 스크린샷 저장 (call 단계)
    if rep.when == "call" and rep.failed and driver:
        screenshot_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        file_path = os.path.join(screenshot_dir, f"{item.name}.png")
        driver.save_screenshot(file_path)
        print(f"\nScreenshot saved to: {file_path}")

    # TestRail 업로드 (call 단계에서만)
    if rep.when != "call":
        return

    enabled = item.config.getoption("--testrail-upload").lower() == "true"
    # fixture를 테스트 코드에서 명시적으로 받지 않아도 hook에서 강제로 읽기
    run_id = item._request.getfixturevalue("testrail_run_id")

    if not enabled or not run_id:
        return  # 업로드 비활성 또는 run_id 없음

    # case_id 마커 읽기: @pytest.mark.case_id(<id>)
    m = item.get_closest_marker("case_id")
    if not m or not m.args:
        return  # 마커 없으면 업로드 스킵

    case_id = int(m.args[0])

    if rep.passed:
        status_id = 1  # Passed
    elif rep.failed:
        status_id = 5  # Failed
    else:
        status_id = 2  # Blocked

    cfg = {
        "base_url": os.getenv("TESTRAIL_URL"),
        "email": os.getenv("TESTRAIL_EMAIL"),
        "api_key": os.getenv("TESTRAIL_API_KEY"),
    }

    ok, msg = _testrail_add_result_for_case(
        cfg, run_id, case_id, status_id, comment=f"pytest nodeid: {item.nodeid}"
    )
    if not ok:
        print(f"[TestRail] upload failed: {msg}")


# ==========================
# TestRail API helper
# ==========================
def _testrail_add_result_for_case(cfg, run_id: int, case_id: int, status_id: int, comment: str = ""):
    if not (cfg.get("base_url") and cfg.get("email") and cfg.get("api_key")):
        return False, "Missing TESTRAIL_URL/EMAIL/API_KEY env"

    url = f"{cfg['base_url'].rstrip('/')}/index.php?/api/v2/add_result_for_case/{run_id}/{case_id}"
    payload: dict[str, object] = {"status_id": status_id}
    if comment:
        payload["comment"] = comment

    r = requests.post(
        url,
        json=payload,
        auth=HTTPBasicAuth(cfg["email"], cfg["api_key"]),
        timeout=15,
    )
    if r.status_code >= 300:
        return False, f"{r.status_code} {r.text[:200]}"
    return True, "OK"