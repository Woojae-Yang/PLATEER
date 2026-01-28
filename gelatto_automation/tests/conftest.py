# tests/conftest.py
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

#%% #########################################################

import pytest

from setup.driver_setup import create_driver
from setup.testrail_client import TestRailClient
from test_flow import MainFlow

from actions.gelatto_action import GelattoAction
from actions.chatbot_action import ChatbotAction


@pytest.fixture(scope="session")
def driver_wait():
    """브라우저 세션 1회 생성/종료"""
    driver, wait = create_driver()
    yield driver, wait
    driver.quit()


@pytest.fixture(scope="session")
def flow(driver_wait):
    """
    로그인 + Gelatto 탭 + blank 탭 + Shop->Chatbot 진입까지
    (전체 E2E 공통 준비)
    """
    driver, wait = driver_wait
    mainflow = MainFlow(driver, wait)
    mainflow.prepare_main()
    yield mainflow


@pytest.fixture(scope="function")
def gelatto(flow):
    """
    Gelatto 탭을 사용하는 Action만 제공
    - 필요 테스트만 gelatto fixture를 받으면 됨
    """
    driver = flow.driver
    wait = flow.wait
    action = GelattoAction(driver, wait, flow.gelatto_tab)
    action.gelatto.switch_tab()
    return action


@pytest.fixture(scope="function")
def chatbot(flow):
    """
    Chatbot 탭을 사용하는 Action만 제공
    """
    driver = flow.driver
    wait = flow.wait
    action = ChatbotAction(driver, wait, flow.chatbot_tab)
    action.chatbot.switch_tab()
    return action

# ##################################################################
# [TestRail 결과 수집]
# ##################################################################

from setup.config_loader import ConfigLoader
from setup.testrail_client import TestRailClient

from datetime import datetime

# TestRail status_id (기본값)
STATUS_PASSED = 1
STATUS_FAILED = 5
STATUS_RETEST = 4  # skip/xfail 등 필요 시 사용

def pytest_configure(config):
    # 실행 중 누적 저장소
    config._testrail_results = []   # [{"case_id":..., "status_id":..., "comment":...}]
    config._testrail_case_ids = set()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # 실제 테스트 함수(call) 결과만 처리
    if report.when != "call":
        return

    marker = item.get_closest_marker("testrail")
    if not marker:
        return

    # case_ids 우선, 없으면 case_id fallback
    raw_case_ids = marker.kwargs.get("case_ids")
    if raw_case_ids is None:
        raw_case_ids = marker.kwargs.get("case_id")
    if not raw_case_ids:
        return
    
    # 항상 list[int]로 정규화
    if isinstance(raw_case_ids, (list, tuple, set)):
        case_ids = [int(x) for x in raw_case_ids]
    else:
        case_ids = [int(raw_case_ids)]

    # pytest 결과 -> TestRail status 매핑
    if report.passed:
        status_id = STATUS_PASSED
    elif report.failed:
        status_id = STATUS_FAILED
    else:
        status_id = STATUS_RETEST

    comment = (
        f"nodeid: {item.nodeid}\n"
        f"result: {report.outcome}\n"
        f"time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # 복수 case_id 모두 results에 넣기
    for cid in case_ids:
        item.config._testrail_case_ids.add(cid)
        item.config._testrail_results.append({
            "case_id": cid,
            "status_id": status_id,
            "comment": comment,
        })

def pytest_sessionfinish(session, exitstatus):
    config = session.config

    # testrail 마커 붙은 테스트가 없으면 아무 것도 안 함
    results = getattr(config, "_testrail_results", [])
    if not results:
        return

    cfg = ConfigLoader()
    if not cfg.testrail_enabled:
        return

    run_id = cfg.testrail_run_id
    if not run_id:
        raise RuntimeError("testrail.run.id is missing in config.yaml (need run_id for direct upload)")

    tr = TestRailClient(cfg)
    tr.add_results_for_cases(run_id=run_id, results=results)

