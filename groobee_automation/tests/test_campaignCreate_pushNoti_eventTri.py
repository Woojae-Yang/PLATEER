import time
import pytest
from selenium.common import JavascriptException, WebDriverException, NoSuchElementException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utilities.BaseClass import BaseClass
from PageObjects.PushNotiPage import PushNotiPage

#@pytest.fixture(scope="module")
#def testrail_run_id():
#    return 001   # 이 파일의 TestRail Run ID

@pytest.mark.usefixtures("driver", "login")
class TestCampaignCreate(BaseClass):

    campaign_brower_title= "푸시 알림 캠페인 :: GROOBEE"
    campaign_brower_expect_title = "새로운 캠페인 만들기 :: GROOBEE"  # 이벤트 트리거
    campaign_regist_title = "새로운 푸시 알림 캠페인 만들기" # 만들기, 복사하기 동일
    expect_modify_title = "푸시 알림 캠페인 수정 하기 :: GROOBEE"
    expect_copy_title = "새로운 캠페인 만들기 :: GROOBEE"
    # 1단계
    event_Tri_campaign_name = "[HS][Auto] 푸시_이벤트 트리거 캠페인"
    event_Tri_expected_campaign_name = "[HS][Auto] 푸시_이벤트 트리거 캠페인"
    event_Tri_expected_title = "푸시 이벤트 트리거 캠페인"
    event_Tri_campaign_des = " 자동화_이벤트 트리거"
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
    onsite_seg_id = "[QA][HS] onsite_브라우저_크롬"
    expected_file_name = "pushNoti_test_img.jpg"
    expected_file_name_member = "push_sample (37).csv"

    webBrowser = "https://groobee.shop/product/list.html?cate_no=25"
    Offsite_advanced_key = "초코"
    Offsite_advanced_value = "누텔라"

 # ======== case 1 . 푸시 알림 캠페인 페이지 노출  =======
    @pytest.mark.case_ids(5000)
    def test_5000(self, driver):
        groobee = PushNotiPage(driver)

        # 1. 푸시 알림 캠페인 LNB 클릭
        groobee.click_pushnoti_menu()
        time.sleep(1)

        # 1. 푸시 알림 캠페인 페이지 노출 확인 _브라우저 타이틀
        assert driver.title == self.campaign_brower_title
        # 2. 이벤트 트리거 탭 클릭
        groobee.click_eventTrigger_send_tab()
        time.sleep(1)
        # 2-1. 진행 중 캠페인 중지
        campaign_name = self.event_Tri_campaign_name
        rows = driver.find_elements(
            By.XPATH,
            f"//tr[.//td[contains(.,'{campaign_name}')]]"
        )
        if not rows:
            print("캠페인 자체가 없음 → PASS")
        else:
            groobee.click_play_icon_by_name(campaign_name)

            try:
                WebDriverWait(driver, 3).until(
                    EC.visibility_of_element_located(groobee.dialog_confirm_btn)
                )
                groobee.click_dialog_confirm_btn()
            except TimeoutException:
                print("다이얼로그 없음 → 이미 중지 상태 → PASS")

    @pytest.mark.case_id(5001)
    def test_5001(self, driver):
        groobee = PushNotiPage(driver)
        # 1. 만들기 버튼 클릭
        groobee.click_create_pushnoti_btn()
        time.sleep(1)
        # 2. 이벤트 트리거 발송 선택
        groobee.click_create_btn_push_eventTri()
        time.sleep(1)
        # 2-1. 새로운 푸시 알림 캠페인 만들기 페이지 노출 확인
        assert driver.title == self.campaign_brower_expect_title
        time.sleep(1)

    @pytest.mark.case_ids(5002)
    def test_5002(self, driver):
        groobee = PushNotiPage(driver)

        # 1. 캠페인 명, 상세 설명 입력
        groobee.send_cam_name(self.event_Tri_campaign_name)
        groobee.send_cam_des(self.event_Tri_campaign_des)
        time.sleep(1)

        # 1-1. 캠페인 명, 상세 설명 입력 일치 확인
        assert groobee.get_cam_name() == self.event_Tri_campaign_name
        assert groobee.get_cam_des() == self.event_Tri_campaign_des

    @pytest.mark.case_ids(5003)
    def test_5003(self, driver):
        groobee = PushNotiPage(driver)

        # 1. 태그 추가 버튼 클릭
        groobee.click_addtag_btn()
        # 1-1. 엔터 > 텍스트필드 태그 입력
        groobee.send_tag_input(self.tag_input)
        # 1-2. 추가 버튼 클릭
        groobee.click_tag_add()
        # 1-2. 태그 노출 확인
        assert groobee.wait_tag_visible(self.tag_input)

    @pytest.mark.case_ids(5004)
    def test_5004(self, driver):
        groobee = PushNotiPage(driver)

        # 1. 타겟 설정 > expandMore btn
        groobee.click_target_expand()
        time.sleep(1)

        # 1-1. 세그먼트 불러오기 btn
        groobee.click_seg_load()
        time.sleep(1)

        # 1-2. 검색 > 세그먼트 입력
        groobee.send_seg_input(self.onsite_seg_id)
        time.sleep(1)

        # 즐겨찾기 버튼 축소 후 클릭
        groobee.click_favorite_collapse_icon()
        time.sleep(1)

        # 1-3. 검색 > 리스트 [0] 선택
        seg_list = groobee.get_seg_list_onsite()
        assert len(seg_list) > 0, "세그먼트 미노출"
        groobee.click_first_seg_onsite()
        time.sleep(1)
        # 1-4. 선택 btn 실행
        groobee.click_select_btn()

        # 1-5. 세그먼트 입력 == 노출 일치
        groobee.assert_is_onsite_seg(self.onsite_seg_id)
        time.sleep(1)

    @pytest.mark.case_ids(5005)
    def test_5005(self, driver):
        groobee = PushNotiPage(driver)

    # 트리거 설정
    # 1-1. 이벤트 클릭
        groobee.click_event_select_box()
    # 1-2. 리스트 > 장바구니 행동
        groobee.click_cart_option()
    # 2-1. 조건 > 담은 상품명 클릭
        groobee.click_condition_option_product_name()
    # 2-2. 드롭 다운 내 스크롤
        groobee.scroll_to_oper()
        time.sleep(1)
    # 2-3. 선택해주세요 > 다음 중 포함하는게 있음
        groobee.click_condition_operator_any_contains()
    # 2-4. 텍스트 박스 > 문자열(string) 입력 > 파일로 업로드
    # 2-5. 파일 RNB 노출 > 파일 업로드

    @pytest.mark.case_ids(5006)
    def test_5006(self, driver):
        groobee = PushNotiPage(driver)
    # 대기 시간 설정
    # 1-1. 대기 시간  > 즉시
    # 1-2. [다음 단계] btn

    @pytest.mark.case_ids(5007)
    def test_5007(self, driver):
        groobee = PushNotiPage(driver)

    # 2단계 > 광고성

    # 1. 메시지 작성 - 제목, 내용 입력
    # 1-1. 미리보기- 메시지 작성 일치 확인
    # 2. 수신거부 표기 입력
    # 2-1. 미리보기- 수신거부 표기 일치 확인

    @pytest.mark.case_ids(5008)
    def test_5008(self, driver):
        groobee = PushNotiPage(driver)
    # 1. 기본 이미지
    # 1-1. 설정 값 사용 체크
    # 2. 본문 이미지
    # 2-1. 메시지 작성 > 본문 이미지 파일명 일치 확인

    @pytest.mark.case_ids(5009)
    def test_5009(self, driver):
        groobee = PushNotiPage(driver)

    # 1. 클릭 동작
    # 1-1. 딥 링크
    # 1-2. 딥 링크 값 일치 확인

    @pytest.mark.case_ids(5010)
    def test_5010(self, driver):
        groobee = PushNotiPage(driver)

    # 1. 고급 옵션
    # 1-1. 옵션 추가 > value, key 입력
    # 1-2. value , key 값 일치 확인

    @pytest.mark.case_ids(5011)
    def test_5011(self, driver):
        groobee = PushNotiPage(driver)

    # [다음 단계] btn
    # 1. 옵션 설정
    # 1-1. 수동 종료 전까지 클릭

    @pytest.mark.case_ids(5012)
    def test_5012(self, driver):
        groobee = PushNotiPage(driver)

    # [저장] btn 실행
    # 이벤트 트리거 발송 tab 클릭
    # 리스트 > 서치 바
    # 해당 캠페인 검색
    #


