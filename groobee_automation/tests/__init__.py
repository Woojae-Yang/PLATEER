import time
import pytest
from selenium.common import JavascriptException, WebDriverException, NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utilities.BaseClass import BaseClass
from PageObjects.PushNotiPage import PushNotiPage

@pytest.fixture(scope="module")
def testrail_run_id():
    return nn   # 이 파일의 TestRail Run ID

@pytest.mark.usefixtures("driver", "login")
class TestCampaignCreate(BaseClass):

    Campaign_brower_title= "푸시 알림 캠페인 :: GROOBEE"
    campaign_brower_expect_title = "새로운 캠페인 만들기 :: GROOBEE"  # 푸시 알림 캠페인
    campaign_regist_title = "새로운 푸시 알림 캠페인 만들기" # 만들기, 복사하기 동일
    expect_modify_title = "푸시 알림 캠페인 수정 하기 :: GROOBEE"
    expect_copy_title = "새로운 캠페인 만들기 :: GROOBEE"
    # 1단계
    Tri_campaign_name = "[HS][Auto] 푸시_이벤트 트리거 캠페인"
    Tri_expected_campaign_name = "[HS][Auto] 푸시_이벤트 트리거 캠페인"
    Tri_expected_title = "푸시 이벤트 트리거 캠페인"
    Tri_campaign_des = " 광고성,기본 및 본문 이미지, 딥링크, 고급 옵션"
    # 1단계
    # 트리거 설정 - 이벤트
    # 트리거 설정 - 조건
    # 대기 시간 설정 - 대기 시간
    # 추가 필터 이벤트 설정
    # 메시지 발송 제어
    
    # 1단계 - add
    tag_input = "Automation"
    automation_text = "[Auto]"
    Copy_campaign = "-COPY"
    Edit_campaign = "-EDIT"
    # 2단계
    subtitle_message = "메시지 기본 설정"
    subtitle_option = "스케줄"
    ad_type_str = "광고성"
    info_type_str = "정보성"
    Tri_message_title = "푸시 알림 캠페인-이벤트 트리거"
    Tri_message_contents = "내용: 이벤트 트리거 발송 테스트"
    Tri_unsubscribe_notice = "[Auto] 수신 거부 070"
    Offsite_seg_id = "[QA][HS] OFFSITE_회원ID_세그먼트용"
    expected_file_name = "pushNoti_test_img.jpg"
    expected_file_name_member = "push_sample (37).csv"
    deepLink_AOS = "groobee://campaign/detail?id=12"
    deepLink_iOS = "https://app.groobee.io/campaign/detail?id=45"
    webBrowser = "https://groobee.shop/product/list.html?cate_no=25"
    Offsite_advanced_key = "초코"
    Offsite_advanced_value = "누텔라"
