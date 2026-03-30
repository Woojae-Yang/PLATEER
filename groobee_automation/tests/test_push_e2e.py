import pytest
import time
from appium.webdriver.common.appiumby import AppiumBy

@pytest.mark.usefixtures("mobile_driver")
class TestPushReceive:

    @pytest.mark.case_id(18000)
    def test_push_receive_and_open_app(self,  mobile_driver):

        # -----------------------------
        # 2️⃣ Mobile → 알림센터 열기
        # -----------------------------
        mobile_driver.open_notifications()
        time.sleep(2)

        # -----------------------------
        # 3️⃣ Push polling (최대 60초)
        # -----------------------------

        notification = None
        start_time = time.time()

        while time.time() - start_time < 50:

            try:
                notification = mobile_driver.find_element(
                    AppiumBy.ANDROID_UIAUTOMATOR,
                    'new UiSelector().textContains("내용: 스케쥴 발송 테스트")'
                )
                break

            except:
                print("푸시 미도착 → scroll 탐색")

                try:
                    mobile_driver.find_element(
                        AppiumBy.ANDROID_UIAUTOMATOR,
                        'new UiScrollable(new UiSelector().scrollable(true)).scrollForward()'
                    )
                except:
                    pass

                time.sleep(3)

        assert notification is not None, "푸시 알림을 찾지 못했습니다."

        print("푸시 발견")

        # -----------------------------
        # 4️⃣ 푸시 클릭
        # -----------------------------

        notification.click()

        time.sleep(5)

        # -----------------------------
        # 앱 실행 검증
        # -----------------------------
        current_package = mobile_driver.current_package

        assert current_package == "com.android.settings", \
            f"앱 실행 실패: {current_package}"

        print("푸시 클릭 → 앱 실행 성공")