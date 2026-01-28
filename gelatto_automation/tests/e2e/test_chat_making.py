
import pytest
from datetime import datetime

from actions.gelatto_action import GelattoAction
from actions.chatbot_action import ChatbotAction

@pytest.fixture
def time_stamp():
    now = datetime.now()
    return {
        "now": now,
        "ymd": now.strftime("%y%m%d"),
        "hms": now.strftime("%H:%M:%S")
    }

CASES = [
    pytest.param(16654, "h1",
        lambda time_stamp: f"[AUTO]대표문구_{time_stamp['ymd']}",
        id="h1"
    ),
    pytest.param(16655, "hello",
        lambda time_stamp: f"[AUTO]첫인사_{time_stamp['hms']}",   # ← 길이 줄이려면 now 전체 말고 포맷 추천
        id="hello"
    ),
    pytest.param(16656, "placeholder",
        lambda time_stamp: f"[AUTO]Placeholder_{time_stamp['ymd']}",
        id="placeholder"
    ),
]

# 챗봇에 출력되는 문구 확인
@pytest.mark.chatbot
@pytest.mark.parametrize("case_id, key, expected_result", CASES)
def test_chatbot_texts(gelatto, chatbot, time_stamp, case_id, key, expected_result, request):
    # TestRail 마커를 케이스별로 주입
    request.node.add_marker(pytest.mark.testrail(case_id=case_id))

    gelatto.make_gelatto(
        f'[AUTO]대표문구_{time_stamp['ymd']}', 
        f'[AUTO]첫인사_{time_stamp['hms']}', 
        f'[AUTO]Placeholder_{time_stamp['ymd']}'
        )
    h1, hello, placeholder = chatbot.get_chatbot_txt()
    
    actual = {"h1": h1, "hello": hello, "placeholder": placeholder}[key]
    expected = expected_result(time_stamp)

    assert actual == expected

