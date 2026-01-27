
import pytest
from datetime import datetime

from actions.gelatto_action import GelattoAction

@pytest.mark.gelatto
@pytest.mark.testrail(case_id=20877)
def test_glossary(gelatto): # LNB [용어사전]
    """
    prepared(conftest fixture)에서 이미 MainFlow.prepare_main()까지 끝났다고 가정.
    prepared가 최소한 아래 키를 제공하면 됨:
      - driver
      - wait
      - gelatto_tab
    """

    # 실행 (예외 없이 끝나면 PASS)
    gelatto.register_topic()
    gelatto.register_word()