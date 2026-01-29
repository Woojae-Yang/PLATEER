import pytest

from actions.gelatto_action import GelattoAction

CASES = [
    pytest.param(16664, "dashboard title", "대시보드", id = "dashboard title")
    , pytest.param(16665, "chatbot subtitle", "AI 챗봇", id = "chatbot subtitle" )
    , pytest.param(16666,  "last updated", )
    , pytest.param( )
    , pytest.param( )
]

@pytest.mark.gelatto
@pytest.mark.parametrize("case_id, key, expected_result", CASES)
def test_dashboards_ui(gelatto):
    gelatto.get_dashboard_ui()

