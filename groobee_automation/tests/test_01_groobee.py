import pytest

from PageObjects.CampaignPage import CampaignPage
from PageObjects.RecommendPage import RecommendPage


class TestGroobee:
    login_expect_title = "대시보드 :: GROOBEE"
    segment_expect_title = "세그먼트 타겟팅 :: GROOBEE"
    segment_regist_expect_title = "새로운 세그먼트 만들기 :: GROOBEE"
    onsiteweb_segment_name = "[QA] 온사이트웹-현재-PC접속 테스트 세그먼트"
    onsite_expect_title = "온사이트 캠페인 :: GROOBEE"

    @pytest.mark.case_id(16658)
    def test_login(self, driver, login):
        assert driver.title == self.login_expect_title

    def test_campaign_clear(self, driver, clear_campaigns):
        groobee = CampaignPage(driver)

        groobee.click_campaign_menu()
        clear_campaigns(groobee)

        groobee.click_recommend_menu()
        clear_campaigns(groobee)

        groobee.click_pushnoti_menu()
        clear_campaigns(groobee)

        groobee.click_kakaobrand_menu()
        clear_campaigns(groobee)

        groobee.click_kakaoalim_menu()
        clear_campaigns(groobee)

        groobee.click_sms_menu()
        clear_campaigns(groobee)