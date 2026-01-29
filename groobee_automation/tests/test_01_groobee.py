import pytest

from PageObjects.SegmentPage import SegmentPage

class TestGroobee:
    login_expect_title = "대시보드 :: GROOBEE"
    segment_expect_title = "세그먼트 타겟팅 :: GROOBEE"
    segment_regist_expect_title = "새로운 세그먼트 만들기 :: GROOBEE"
    onsiteweb_segment_name = "[QA] 온사이트웹-현재-PC접속 테스트 세그먼트"

    @pytest.mark.case_id(16658)
    def test_login(self, driver, login):
        assert driver.title == self.login_expect_title

    @pytest.mark.case_id(16659)
    def test_segment_move(self, driver):
        groobee = SegmentPage(driver)

        # LNB > 세그먼트 타겟팅 메뉴 선택

        # 세그먼트 타겟팅 페이지 [표시 확인]
        # assert groobee.wait__loaded()
        assert driver.title == self.segment_expect_title

    @pytest.mark.case_id(16660)
    def test_segment_regist_move(self, driver):
        groobee = SegmentPage(driver)

        # 만들기 버튼 선택

        # 새로운 세그먼트 만들기 페이지 [표시 확인]
        # assert groobee.wait__loaded()
        assert driver.title == self.segment_regist_expect_title

    @pytest.mark.case_id(16661)
    def test_segment_regist_rnb(self, driver):
        groobee = SegmentPage(driver)

        # 세그먼트명 입력 필드 > "[QA] 온사이트웹-현재-PC접속 테스트 세그먼트" 입력
        # 타겟 설정 > 온사이트(웹/하이브리드) > 현재 > AND/OR 선택
        # 세그먼트 변수 추가 버튼 선택

        # 세그먼트 변수 RNB [노출 확인]
        # assert groobee.wait__loaded()
        # assert

    @pytest.mark.case_id(16662)
    def test_segment_regist_rnb_save(self, driver):
        groobee = SegmentPage(driver)

        # 시스템 선택 > 접속 디바이스 선택 > 선택 버튼 선택
        # 세그먼트 선택 > "PC" > "일 때" 입력
        # 저장 버튼 선택

        # 세그먼트 타겟팅 페이지 [표시 확인]

    @pytest.mark.case_id(16663)
    def test_segment_created(self, driver):
        groobee = SegmentPage(driver)

        # "[QA] 온사이트웹-현재-PC접속 테스트 세그먼트"[표시 확인]
        # assert