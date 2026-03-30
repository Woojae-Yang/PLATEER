import os
import pytest
import requests
import time
import subprocess
import signal
import platform
from datetime import datetime

from seleniumwire import webdriver 
# api 테스트에서 webdriver 활용을 위해 selenium-wire 라이브러리로 변경, 다른 영역은 기존의 selenium과 호환 가능

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from appium import webdriver as appium_webdriver
from appium.options.android import UiAutomator2Options
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

    # 화면 녹화 옵션
    parser.addoption("--record-video", action="store", default="false")  # true/false
    parser.addoption("--video-pre", action="store", default="3")  # 실패 전 n초
    parser.addoption("--video-post", action="store", default="3")  # 실패 후 n초


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
    record_video = request.config.getoption("--record-video").lower() == "true"

    # ✅ 녹화(B안)일 땐 Docker에서도 headless 끄기 (Xvfb에 실제 렌더링되게)
    headless_enabled = (in_docker or cli_headless) and (not record_video)

    # Chrome 옵션 설정
    options = ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=ko-KR")
    options.add_argument("--accept-lang=ko-KR")
    options.add_argument("Accept-Language=ko-KR")

    # ✅ Docker/헤드리스/녹화(Xvfb)에서는 고정 해상도 필요
    if in_docker or headless_enabled or record_video:
        options.add_argument("--window-size=2560,1440")

    options.add_experimental_option("perfLoggingPrefs", {"enableNetwork": True})
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    if headless_enabled:
        options.add_argument("--headless=new")

    # 드라이버 경로 설정
    if in_docker:
        driver_path = "/usr/local/bin/chromedriver"
        service = Service(driver_path)
    else:
        from webdriver_manager.chrome import ChromeDriverManager

        driver_path = ChromeDriverManager().install()
        if driver_path.endswith("THIRD_PARTY_NOTICES.chromedriver"):
            driver_path = driver_path.replace("THIRD_PARTY_NOTICES.chromedriver", "chromedriver")

        service = Service(driver_path)

    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)

    # ✅ 로컬(headful)에서는 최대화 (headless/도커/녹화에서는 금지)
    if (not in_docker) and (not headless_enabled) and (not record_video):
        try:
            driver.maximize_window()
        except Exception:
            pass

    yield driver
    driver.quit()

@pytest.fixture(autouse=True)
def video_recording(request):
    """
    목적:
      - 테스트 함수(item) 단위로 녹화를 시작/종료한다.
      - FAIL일 때만 (failure_elapsed 기준 pre/post 클립) 저장한다.
      - PASS면 원본(mp4) 삭제한다.
    """
    item = request.node  # 이 item이 makereport의 item과 동일(핵심)

    record_enabled = item.config.getoption("--record-video").lower() == "true"
    if not record_enabled:
        yield
        return

    # class-scope driver를 받아와서 사용 (세션/로그인 공유 유지)
    driver = request.getfixturevalue("driver")

    # start: item(함수) 기준으로 녹화 시작
    _start_video_recording(item, driver)

    yield

    # teardown: FAIL 여부를 보고 저장/삭제
    failed = getattr(item, "_was_failed", False)
    _stop_and_save_video(item, failed=failed)

def _start_video_recording(item, driver):
    record_enabled = item.config.getoption("--record-video").lower() == "true"
    if not record_enabled:
        return

    if platform.system() != "Linux":
        print("[VIDEO] Recording supported only on Linux/X11 (Docker/Server)")
        return

    display = os.getenv("DISPLAY")
    if not display:
        print("[VIDEO] DISPLAY not set. Skipping recording.")
        return

    os.makedirs("videos/tmp", exist_ok=True)

    test_name = item.name
    temp_path = f"videos/tmp/{test_name}_full.mp4"
    log_path = f"videos/tmp/{test_name}.ffmpeg.log"

    # ✅ xvfb-run screen size와 반드시 일치해야 함 (Dockerfile에서 2560x1440)
    video_size = "2560x1440"

    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel", "error",
        "-video_size", video_size,
        "-framerate", "25",
        "-f", "x11grab",
        "-i", display,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        temp_path,
    ]

    log_f = open(log_path, "wb")
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=log_f,
    )

    time.sleep(0.2)
    if process.poll() is not None:
        try:
            log_f.flush()
            log_f.close()
        except Exception:
            pass
        print(f"[VIDEO] ffmpeg exited immediately (rc={process.returncode}). See {log_path}")
        return

    item._video_process = process
    item._video_start_time = datetime.now()
    item._video_temp_path = temp_path
    item._video_log_path = log_path
    item._video_log_f = log_f

    # ✅ FAIL/PASS 처리 플래그 초기화
    item._was_failed = False
    item._failure_elapsed = None


def _stop_and_save_video(item, failed: bool):
    if not hasattr(item, "_video_process"):
        return

    process = item._video_process

    pre = int(item.config.getoption("--video-pre"))
    post = int(item.config.getoption("--video-post"))

    # ✅ 실패면 post초 확보 (뒤 3초)
    if failed and post > 0:
        time.sleep(post)

    # ✅ 정상 종료(중요): SIGINT -> wait
    try:
        if process.poll() is None:
            process.send_signal(signal.SIGINT)
        try:
            process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)
    finally:
        try:
            if getattr(item, "_video_log_f", None):
                item._video_log_f.close()
        except Exception:
            pass

    # PASS면 원본 삭제(정책)
    if not failed:
        if os.path.exists(item._video_temp_path):
            os.remove(item._video_temp_path)
        return

    # 원본이 0바이트면 컷팅할 의미 없음 → 로그 확인
    if (not os.path.exists(item._video_temp_path)) or os.path.getsize(item._video_temp_path) == 0:
        print(f"[VIDEO] raw mp4 is empty: {item._video_temp_path}")
        print(f"[VIDEO] check ffmpeg log: {getattr(item,'_video_log_path','(no log)')}")
        return

    # ✅ 컷 기준은 "실패 판정 순간" (makereport(call)에서 저장된 값)
    failure_elapsed = getattr(item, "_failure_elapsed", None)
    if failure_elapsed is None:
        failure_elapsed = (datetime.now() - item._video_start_time).total_seconds()

    start_cut = max(failure_elapsed - pre, 0)
    duration = pre + post

    os.makedirs("videos", exist_ok=True)
    final_path = f"videos/{item.name}.mp4"

    # ✅ 재인코딩 컷팅(안정): -c copy 금지 (키프레임/짤림 방지)
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel", "error",
        "-ss", str(start_cut),
        "-i", item._video_temp_path,
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        final_path,
    ]
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if r.returncode != 0:
        print("[VIDEO] cut/encode failed:")
        print(r.stderr.decode("utf-8", errors="ignore"))

    try:
        os.remove(item._video_temp_path)
    except FileNotFoundError:
        pass

    if (not os.path.exists(final_path)) or os.path.getsize(final_path) == 0:
        print(f"[VIDEO] final mp4 is empty: {final_path}")
        print(f"[VIDEO] check ffmpeg log: {getattr(item,'_video_log_path','(no log)')}")
        return

    print(f"[VIDEO] Saved failure clip: {final_path}")

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

# ========================
# Appium
# ========================

@pytest.fixture(scope="class")
def mobile_driver():

    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "Android"

    options.app_package = "com.android.settings"
    options.app_activity = ".Settings"

    driver = appium_webdriver.Remote(
        "http://127.0.0.1:4723",
        options=options
    )
    yield driver
    driver.quit()

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

    # ✅ FAIL 시점만 기록 (종료/저장은 video_recording fixture teardown에서 1회 수행)
    if rep.failed and rep.when in ("setup", "call"):
        item._was_failed = True
        if hasattr(item, "_video_start_time"):
            item._failure_elapsed = (datetime.now() - item._video_start_time).total_seconds()

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

def pytest_configure(config):
    config.addinivalue_line("markers", "case_id(id): TestRail case ID")
    config.addinivalue_line("markers", "case_ids(ids): TestRail 복수 case ID 등록용 (리스트 가능)") # 0225 추가
    config.addinivalue_line("markers", "testrail(kwargs): TestRail 통합 마커 (case_ids=[...] 형태)") # 0225 추가
    config.addinivalue_line("markers", "run_id(id): TestRail run ID")  # 0225 추가