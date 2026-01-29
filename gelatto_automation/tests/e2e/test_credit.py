import pytest

@pytest.mark.gelatto
@pytest.mark.parametrize("case_id, key, expected_result", CASES)
def check_credit():
    