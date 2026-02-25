import os
import pytest
import requests
import time

from seleniumwire import webdriver 
# api 테스트에서 webdriver 활용을 위해 selenium-wire 라이브러리로 변경, 다른 영역은 기존의 selenium과 호환 가능

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
@pytest.fixture(scope="class")  # session -> class 0225 변경
def testrail_run_id(request):
    # 1) CLI 우선
    cli = request.config.getoption("--testrail-run-id")
    if cli:
        return int(cli)

    # 2) 클래스(또는 상위) 마커에서 run_id 읽기
    marker = request.node.get_closest_marker("run_id")
    if marker and marker.args:
        return int(marker.args[0])

    # 3) .env fallback
    env = os.getenv("TESTRAIL_RUN_ID")
    return int(env) if env else None

## 범위를 session -> class 변경 260204
@pytest.fixture(scope="class")
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

    options.add_experimental_option("perfLoggingPrefs", {"enableNetwork": True})
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    if headless_enabled:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=2560,1440")

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
    driver.implicitly_wait(10)

    # 로컬(비 headless)일 때만 maximize
    if not headless_enabled:
        driver.maximize_window()

    yield driver
    driver.quit()

## 범위를 session -> class 변경 260204
@pytest.fixture(scope="class")
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
    time.sleep(1)

    groobee = LoginPage(driver)
    time.sleep(1)

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
# TestRail API helper
# ==========================

def _get_testrail_cfg():
    return {
        "base_url": os.getenv("TESTRAIL_URL"),
        "email": os.getenv("TESTRAIL_EMAIL"),
        "api_key": os.getenv("TESTRAIL_API_KEY"),
    }


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

# 테스트 코드에서 중간 단계 결과를 직접 업로드할 때 호출하는 함수
def upload_result(run_id: int, case_id: int, passed: bool):
    if passed:
        status_id = 1  # Passed
    elif passed is False:
        status_id = 5  # Failed
    else:
        status_id = 2  # Blocked
    cfg = _get_testrail_cfg()
    ok, msg = _testrail_add_result_for_case(cfg, run_id, case_id, status_id)
    if not ok:
        print(f"[TestRail] upload failed: {msg}")


# ==========================
# Hooks
# ==========================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    driver = item.funcargs.get("driver", None)

    # -------------------------
    # 1.실패 시 스크린샷
    # -------------------------
    if rep.when == "call" and rep.failed and driver:
        screenshot_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        file_path = os.path.join(screenshot_dir, f"{item.name}.png")
        driver.save_screenshot(file_path)
        print(f"\n Screenshot saved: {file_path}")

    # -------------------------
    # 2️⃣ TestRail 업로드는 call 단계에서만
    # -------------------------
    if rep.when != "call":
        return

    enabled = item.config.getoption("--testrail-upload").lower() == "true"
    run_id = item._request.getfixturevalue("testrail_run_id")

    if not enabled:
        print("TestRail upload disabled")
        return

    if not run_id:
        print("No TestRail run_id provided")
        return

    # -------------------------
    # 3️⃣ case_id 수집 (완전 통합)
    # -------------------------
    case_ids = []

    # @pytest.mark.case_id(123)
    for m in item.iter_markers(name="case_id"):
        case_ids.extend(m.args)

    # @pytest.mark.case_ids(123, 456) 또는 ([123,456])
    for m in item.iter_markers(name="case_ids"):
        for arg in m.args:
            if isinstance(arg, (list, tuple, set)):
                case_ids.extend(arg)
            else:
                case_ids.append(arg)

    # @pytest.mark.testrail(case_ids=[...])
    for m in item.iter_markers(name="testrail"):
        raw_ids = m.kwargs.get("case_ids") or m.kwargs.get("case_id")
        if raw_ids:
            if isinstance(raw_ids, (list, tuple, set)):
                case_ids.extend(raw_ids)
            else:
                case_ids.append(raw_ids)

    # 중복 제거 + 정수 변환
    case_ids = list(set(int(x) for x in case_ids))

    if not case_ids:
        print(f"ℹ️ No case_id marker for {item.name}")
        return

    # -------------------------
    # 4️⃣ 상태 매핑
    # -------------------------
    if rep.passed:
        status_id = 1   # Passed
    elif rep.failed:
        status_id = 5   # Failed
    else:
        status_id = 2   # Blocked

    cfg = _get_testrail_cfg()

    # -------------------------
    # 5️⃣ 각 Case별 업로드
    # -------------------------
    for cid in case_ids:
        ok, msg = _testrail_add_result_for_case(
            cfg,
            run_id,
            cid,
            status_id,
            comment=f"pytest nodeid: {item.nodeid}"
        )

        if ok:
            print(f"TestRail uploaded: Case {cid} -> status {status_id}")
        else:
            print(f"Upload failed for Case {cid}: {msg}")

    def pytest_configure(config):
        config.addinivalue_line("markers", "case_id(id): TestRail case ID")
        config.addinivalue_line("markers", "run_id(id): TestRail run ID")  # 0225 추가