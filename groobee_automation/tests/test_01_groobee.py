import pytest

class TestGroobee:
    login_expect_title = "대시보드 :: GROOBEE"

    @pytest.mark.case_id(16658)
    def test_login(self, driver, login):
        assert driver.title == self.login_expect_title

    # @pytest.mark.case_id(case_id)
    # def test_case_name(self, driver)
    # 이어서 E2E 시나리오 작성하기