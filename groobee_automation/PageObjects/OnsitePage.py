# import time
from selenium.webdriver.common.by import By
from utilities.BaseClass import BaseClass
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PageObjects.GroobeeActions import GroobeeActions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import time


class OnsitePage(GroobeeActions):
    # =========================element 선언 영역========================
    # 페이지 타이틀
    report_title = "온사이트 캠페인 분석 리포트 :: GROOBEE"
    list_title = "온사이트 캠페인 :: GROOBEE"

    # 온사이트 캠페인 관리
    create_dropdown_onsite = (By.XPATH, "//li[contains(text(),'온사이트 캠페인')]")
    create_dropdown_inapp = (By.XPATH, "//li[contains(text(),'인앱 메시지 캠페인')]")
    except_btn = (By.XPATH, "//button[contains(text(),'제외 조건 관리')]")
    more_btn =(By.XPATH, "//div[@data-field='box_cell']//button[@type='button']")
    test_campaign = (By.XPATH, "//div[@aria-colindex='2']//p[contains(@class,'MuiTypography-root MuiTypography-body2') and contains(text(), '[QA][자동화]')]")
    list_campaign_loc = (By.XPATH, "(//p[contains(@class,'MuiTypography-root MuiTypography-body2')])[2]")


    # 온사이트 캠페인 만들기
    title = (By.XPATH, "//h1[contains(text(),'새로운 온사이트 캠페인 만들기')]")
    # stepper_step1
    camp_name_sub = (By.XPATH, "//strong[contains(@class, 'MuiTypography-subtitle2') and contains(text(), '캠페인명')]")
    camp_des_sub = (By.XPATH, "//strong[contains(@class, 'MuiTypography-subtitle2') and contains(text(), '상세 설명')]")
    tag_sub = (By.XPATH, "//strong[contains(@class, 'MuiTypography-subtitle2') and contains(text(), '태그')]")
    campaign_name_input = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 40자']")
    campaign_des_input = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 400자']")
    tag_btn = (By.XPATH, "//button[contains(text(),'태그 추가')]")
    plaform_sub = (By.XPATH, "//strong[contains(text(),'플랫폼')]")
    plaform_webhybrid = (By.XPATH, "//p[contains(text(),'웹/하이브리드')]")
    msg_type_sub = (By.XPATH, "//strong[contains(text(),'메시지 유형')]")
    msg_type_layer = (By.XPATH, "//p[contains(text(),'레이어')]")
    access_type_sub = (By.XPATH, "//strong[contains(text(),'접속 유형')]")
    access_type_pc = (By.XPATH, "//*[contains(text(),'PC/웹')]")
    access_type_mo = (By.XPATH, "//*[contains(text(),'모바일 전체')]")
    access_type_mo_web = (By.XPATH, "//*[contains(text(),'모바일 웹')]")
    access_type_mo_app = (By.XPATH, "//*[contains(text(),'모바일 앱')]")

    # common
    com_tag_title = (By.XPATH, "//h2[@id='customized-dialog-title' and text()='태그 추가']")
    com_tag_input = (By.XPATH, "//textarea[@placeholder='엔터로 복수 입력 가능']")
    com_tag_frequency = (By.XPATH, "//button[@id='basic-tab-0' and text()='빈도 순']")
    com_tag_alphabet = (By.XPATH, "//button[@id='basic-tab-1' and text()='가나다 순']")
    com_tag_def = (By.XPATH, "//span[contains(text(), '작성: 그루비샵')]")
    com_tag_cancel_btn = (By.XPATH,"//div[@class='MuiStack-root css-1e8kor0']//button[contains(text(),'취소')]")
    com_tag_add_btn = (By.XPATH,"//div[@class='MuiStack-root css-1e8kor0']//button[contains(text(),'추가')]")
    com_added_tag = (By.XPATH,"//span[contains(@class, 'MuiChip') and contains(text(),'자동화태그')]")

    # 세그먼트
    com_segment = (By.XPATH, "//h6[contains(text(),'[QA][JE] 자동화 세그먼트')]")
    setting_segment = (By.XPATH,"//div[contains(@class,'MuiAccordionSummary-content')]/p")

    # 메시지 설정
    add_btn = (By.XPATH, "//button[contains(text(),'추가')]")
    design_type_popup = (By.XPATH, "//p[contains(text(),'팝업')]']")
    width_size = (By.XPATH, "//input[@id=':r3a:']")
    width_size_list_px = (By.XPATH, "//*[normalize-space()='px']")
    width_size_list_percent = (By.XPATH, "//*[normalize-space()='%']")

    img_link_tgl_on = (By.XPATH,"//div[h6[contains(text(),'이미지 링크')]]//span[contains(@class, 'Mui-checked')]")
    img_link_tgl_off = (By.XPATH,"//div[h6[contains(text(),'이미지 링크')]]//span[not(contains(@class, 'Mui-checked'))]")
    img_link_entire = (By.XPATH, "//span[contains(text(),'이미지 전체')]")
    img_link_map = (By.XPATH, "//span[contains(text(),'이미지 맵 설정')]")
    clk_area_setting_btn = (By.XPATH, "//button[contains(text(),'클릭 영역 설정')]")
    clk_area_setting_title = (By.XPATH, "//div[contains(text(),'클릭 영역 설정')]")
    clk_area_setting_name = (By.XPATH,"//input[@placeholder='한글 공백 포함 최대 20자']")
    clk_area_setting_url = (By.XPATH,"//textarea[@placeholder='http:// 또는 https://를 포함한 URL']")
    preview_area = (By.XPATH,"//div[@class='MuiBox-root css-1sphhkp']//a[@id='view-area1']")
    save_btn = (By.XPATH, "//button[contains(text(),'저장')]")
    act_same = (By.XPATH, "//*[contains(text(),'현재 창으로 열기')]")
    act_new = (By.XPATH, "//*[contains(text(),'새 창으로 열기')]")
    ling_link_textfield = (By.XPATH,"//textarea[@id=':r3d:' and @placeholder='http:// 또는 https://를 포함한 URL']")
    title_tgl_off = (By.XPATH,"//div[h6[contains(text(),'타이틀')]]//span[not(contains(@class, 'Mui-checked'))]")
    title_tgl_on = (By.XPATH,"//div[h6[contains(text(),'타이틀')]]//span[contains(@class, 'Mui-checked')]")
    title_txt_tf = (By.XPATH, "//textarea[@placeholder='한글 공백 포함 최대 40자']")
    blank_font_inherit = (By.XPATH, "//ul[@id=':r40:']//li[@data-value='inherit']")
    blank_font_gothic = (By.XPATH, "//ul[@id=':r40:']//li[@data-value='Malgun Gothic']")
    title_array_left = (By.XPATH,"//div[contains(@class, 'MuiToggleButtonGroup')]//button[@value='left']")
    title_array_center = (By.XPATH,"//div[contains(@class, 'MuiToggleButtonGroup')]//button[@value='center']")
    title_array_right = (By.XPATH,"//div[contains(@class, 'MuiToggleButtonGroup')]//button[@value='right']")
    title_display = (By.XPATH, "//strong[@class='tit_999999']")

    blank_tgl_off = (By.XPATH,"//div[h6[contains(text(),'내용')]]//span[not(contains(@class, 'Mui-checked'))]")
    blank_tgl_on = (By.XPATH,"//div[h6[contains(text(),'내용')]]//span[contains(@class, 'Mui-checked')]")
    blank_txt_tf = (By.XPATH, "@placeholder='한글 공백 포함 최대 80자']")
    blank_font_inherit = (By.XPATH, "//ul[@id=':r43:']//li[@data-value='inherit']")
    blank_font_gothic = (By.XPATH, "//ul[@id=':r43:']//li[@data-value='Malgun Gothic']")
    blank_display = (By.XPATH, "//p[@class='description_999999']")

    btn_tgl_off = (By.XPATH,"//div[h6[contains(text(),'버튼')]]//span[not(contains(@class, 'Mui-checked'))]")
    btn_tgl_on = (By.XPATH,"//div[h6[contains(text(),'버튼')]]//span[contains(@class, 'Mui-checked')]")
    btn_txt_tf = (By.XPATH, "//input[@placeholder='한글 공백 포함 최대 10자']")
    btn_font_inherit = (By.XPATH, "//ul[@id=':r46:']//li[@data-value='inherit']")
    btn_font_gothic = (By.XPATH, "//ul[@id=':r46:']//li[@data-value='Malgun Gothic']")
    btn_url_blank = (By.XPATH,"//textarea[@placeholder='http:// 또는 https:// 또는 {scheme}://를 포함한 URL']")
    btn_display = (By.XPATH, "//a[@id='btn-popup999999']")

    close_tgl_off = (By.XPATH,"//div[h6[contains(text(),'닫기')]]//span[not(contains(@class, 'Mui-checked'))]")
    close_tgl_on = (By.XPATH,"//div[h6[contains(text(),'닫기')]]//span[contains(@class, 'Mui-checked')]")
    do_not_tgl_on = (By.XPATH,"//div[h6[contains(text(),'다시 보지 않기')]]//span[contains(@class, 'Mui-checked')]")
    do_not_tgl_off = (By.XPATH,"//div[h6[contains(text(),'다시 보지 않기')]]//span[not(contains(@class, 'Mui-checked'))]")
    do_not_1day = (By.XPATH, "//*[contains(text(),'1일')]")
    do_not_2day = (By.XPATH, "//*[contains(text(),'2일')]")
    do_not_3day = (By.XPATH, "//*[contains(text(),'3일')]")
    do_not_4day = (By.XPATH, "//*[contains(text(),'4일')]")
    do_not_5day = (By.XPATH, "//*[contains(text(),'5일')]")
    do_not_6day = (By.XPATH, "//*[contains(text(),'6일')]")
    do_not_7day = (By.XPATH, "//*[contains(text(),'7일')]")
    do_not_setting = (By.XPATH, "//span[contains(text(),'기간 없이 설정')]]")
    do_not_background_white = (By.XPATH, "//span[contains(text(),'흰색')]")
    do_not_background_clear = (By.XPATH, "//span[contains(text(),'투명')]")
    do_not_location_botton = (By.XPATH, "//span[contains(text(),'메시지 아래')]")
    do_not_location_top = (By.XPATH, "//span[contains(text(),'메시지 위')]")

    select_style_btn = (By.XPATH, "//button[contains(text(),'스타일 선택')]")
    style_dim = (By.XPATH, "//span[contains(text(),'딤')]")
    style_shadow = (By.XPATH, "//span[contains(text(),'그림자')]")
    animation_none = (By.XPATH, "//div[contains(text(),'없음')]")
    animation_appear = (By.XPATH, "//div[contains(text(),'나타나기')]")
    animation_wipe = (By.XPATH, "//div[contains(text(),'닦아내기')]")
    animation_shrink = (By.XPATH, "//div[contains(text(),'축소하기')]")
    animation_slide_up = (By.XPATH, "//div[contains(text(),'위쪽 슬라이드')]")
    animation_slide_down = (By.XPATH, "//div[contains(text(),'아래쪽 슬라이드')]")
    animation_slide_left = (By.XPATH, "//div[contains(text(),'왼쪽 슬라이드')]")
    animation_slide_right = (By.XPATH, "//div[contains(text(),'오른쪽 슬라이드')]")
    exp_detail = (By.XPATH, "//span[contains(text(),'상세 노출')]")
    exp_topbottom = (By.XPATH, "//span[contains(text(),'상하 노출')]")

    abn_manual = (By.XPATH, "//span[contains(text(),'수동 설정')]")
    abn_ai = (By.XPATH, "//span[contains(text(),'AI 자동화')]")

    # 옵션 설정
    trigger_page_tgl_on = (By.XPATH,"//div[h6[contains(text(),'노출 페이지')]]//span[contains(@class, 'Mui-checked')]")
    trigger_page_tgl_off = (By.XPATH,"(//div[h6[contains(text(),'노출 페이지')]]//span[not(contains(@class, 'Mui-checked'))])[1]")
    trigger_page_url_tf = (By.XPATH,"(//div[strong[text()='URL']]/following-sibling::div//textarea)[1]")
    trigger_page_time_tf = (By.XPATH,"//div[p[contains(text(), '초 이상 봤을 때')]]/preceding-sibling::input[@placeholder='숫자만 입력 가능']")
    trigger_page_scroll_tf = (By.XPATH,"//div[p[contains(text(), '% 이상 봤을 때')]]/preceding-sibling::input[@placeholder='숫자만 입력 가능']")
    tlg_chip = (By.XPATH, "//span[contains(@class,'MuiChip-label')]")

    # 캠페인 노출
    camp_img = (By.XPATH, "//a[@id='image-all-A']//img[@class='img_999999']")
    camp_btn1 = (By.XPATH, "//a[@id='btn-popup-A']")

    # 분석 리포트
    exp_cnt = (By.XPATH, "//div[h6[contains(text(), '노출 수')]]//following-sibling::div")
    clk_cnt = (By.XPATH, "//h6[contains(., '클릭 수')]/ancestor::div[contains(@class, 'MuiPaper-root')]//div[contains(@class, 'subtitle1')]")
    clk_detail = (By.XPATH, "//div[@class='MuiStack-root css-on2uk3']//button[@type='button'][contains(text(),'상세보기')]")
    clk_datail_img_a =(By.XPATH, "//td[contains(text(), '(A안) 이미지 링크')]/following-sibling::td[1]")
    or_cnt_tot = (By.XPATH, "//div[h6[contains(text(), '주문 수')]]//following-sibling::div[1]")
    or_cnt_clk = (By.XPATH, "//div[h6[contains(text(), '주문 수')]]//following-sibling::div[2]")
    conv_amt_cnt_tot = (By.XPATH, "//div[h6[contains(text(), '전환 금액')]]//following-sibling::div[1]")
    conv_amt_cnt_clk = (By.XPATH, "//div[h6[contains(text(), '전환 금액')]]//following-sibling::div[2]")
    clk_conv_per = (By.XPATH, "//h6[contains(., '클릭 전환율')]/ancestor::div[contains(@class, 'MuiPaper-root')]//div[contains(@class, 'subtitle1')]")
    clk_conv_detail = (By.XPATH, "//div[@class='MuiStack-root css-1ro3byo']//button[@type='button'][contains(text(),'상세보기')]")
    signup_conv_tot = (By.XPATH, "//div[h6[contains(text(), '회원가입 전환율')]]//following-sibling::div[1]")
    signup_conv_clk = (By.XPATH, "//div[h6[contains(text(), '회원가입 전환율')]]//following-sibling::div[2]")
    or_conv_tot = (By.XPATH, "//div[h6[contains(text(), '주문 전환율')]]//following-sibling::div[1]")
    or_conv_clk = (By.XPATH, "//div[h6[contains(text(), '주문 전환율')]]//following-sibling::div[2]")
    

    
    # 테스트샵
    test_login = (By.XPATH, "//a[contains(text(),'로그인')]")
    test_id_tf = (By.XPATH, "//fieldset[@class='memberArea']//input[@id='member_id']")
    test_pw_tf = (By.XPATH, "//fieldset[@class='memberArea']//input[@id='member_passwd']")
    test_login_btn = (By.XPATH, "//button[@type='button'][contains(text(),'로그인')]")
    test_product = (By.XPATH, "//img[@id='eListPrdImage34_1']")
    test_buy_btn = (By.XPATH, "//a[contains(@class,'btnSubmitL first')]")
    test_or_name = (By.XPATH, "//input[@id='pname']")
    test_or_bank_list = (By.XPATH, "//select[@id='bankaccount']")
    test_or_bank_list1= (By.XPATH, "//option[contains(text(), '우리은행')]")
    test_or_buy_btn= (By.XPATH, "//button[@id='btn_payment']")
    test_or_agree_btn = (By.XPATH, "//input[@name='chk_purchase_agreement']")
    test_or_comp = (By.XPATH, "//h2[contains(text(),'주문완료')]")


    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    # ========================action 선언 영역========================
    def click_access_type(self, element):
        self.driver.find_element(*element).click()
        return True

    def is_added_tag(self, tag_text, timeout=10):
        locator = (
            By.XPATH,
            f"//span[contains(@class, 'MuiChip') and contains(text(),'{tag_text}')]",
        )
        BaseClass.wait_visible(self.driver, locator, timeout)
        return True

    def is_stepper1(self):
        check_list = [
            self.title,
            self.com_tag_def,
            self.plaform_webhybrid,
            self.msg_type_layer,
        ]

        check_null_list = [self.campaign_name_input, self.campaign_des_input]

        try:
            for locator in check_list:
                WebDriverWait(self.driver, 3).until(
                    EC.visibility_of_element_located(locator)
                )

            for locator in check_null_list:

                input_element = self.driver.find_element(*locator)
                is_null = input_element.get_attribute("value") == ""
                if not is_null:
                    return False
            return True
        except:
            return False

    def click_create_dropdown(self, loc):
        BaseClass.wait_clickable(self.driver, loc).click()

    def is_campaign_reg_title(self, timeout=10):
        return BaseClass.wait_visible(self.driver, self.title, timeout)

    def is_campaign_reg_name(self, timeout=10):
        return BaseClass.wait_visible(self.driver, self.campaign_name_input, timeout)

    def is_campaign_reg_des(self, timeout=10):
        return BaseClass.wait_visible(self.driver, self.campaign_des_input, timeout)

    def is_stepper2(self):
        check_list = [
            self.msg_type_layer,
            self.access_type_pc,
            self.file_uploadBtn,
            self.width_size_list_px,
            self.img_link_tgl_on,
            self.img_link_entire,
            self.act_same,
            self.title_tgl_off,
            self.blank_tgl_off,
            self.btn_tgl_off,
            self.close_tgl_on,
            self.style_dim,
            self.style_shadow,
            self.animation_none,
            self.exp_detail,
            self.abn_manual,
        ]

        for locator in check_list:
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.visibility_of_element_located(locator)
                )
            except:
                print(f"\n [Fail] {locator} not found")

        return True
    
    def is_stepper3(self):

        check_list = [
            self.trigger_page_tgl_off,
            # 추후 추가
        ]

        for locator in check_list:
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.visibility_of_element_located(locator)
                )
            except:
                print(f"\n [Fail] {locator} not found")

        return True

    def is_add_tag_modal(self):
        check_list = [
            self.com_tag_title,
            self.com_tag_input,
            self.com_tag_frequency,
            self.com_tag_alphabet,
            self.com_tag_add_btn,
            self.com_tag_cancel_btn,
        ]

        try:
            for locator in check_list:
                WebDriverWait(self.driver, 3).until(
                    EC.visibility_of_element_located(locator)
                )
            return True
        except:
            return False

    def click_segment(self, seg, timeout=10):
        xpath = f"//h6[contains(text(),'{seg}')]"
        el = BaseClass.wait_visible(self.driver, (By.XPATH, xpath), timeout)
        el.click()

    def is_segment_display(self, timeout=10):
        return BaseClass.wait_clickable(self.driver, self.setting_segment, timeout)

    def is_title_display(self):
        return self.driver.find_element(*OnsitePage.title_display)

    def is_blank_display(self):
        return self.driver.find_element(*OnsitePage.blank_display)

    def is_btn_display(self):
        return self.driver.find_element(*OnsitePage.btn_display)

    def is_camplaign_display(self, name):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, f"//p[contains(text(), '{name}')]")
            )
        )
        return True

    def is_click_setting_area_display(self):
        self.driver.find_element(*OnsitePage.clk_area_setting_title)
        return True

    def is_preview_display(self):
        self.driver.find_element(*OnsitePage.preview_area)
        return True

    def is_upload_image_display(self, img):
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, f"//h6[contains(normalize-space(),'{img}')]")
            )
        )
        return True
    
    
    def is_campaign_display(self, camp, retry=True):
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(camp))
            return True
        except TimeoutException:
            if retry:
                self.driver.refresh()
                return self.is_campaign_display(camp, retry=False)
            return False

    def input_text(self, loc, text, timeout=10):
        el = BaseClass.wait_clickable(self.driver, loc, timeout)
        el.send_keys(text)

    def input_textarea(self, loc, text, timeout=10):
        el = BaseClass.wait_clickable(self.driver, loc, timeout)
        el.send_keys(text)

    def input_url(self, loc, url, timeout=10):
        el = BaseClass.wait_clickable(self.driver, loc, timeout)
        el.send_keys(url)

    def input_chip(self, loc, text, timeout=10):
        el = BaseClass.wait_clickable(self.driver, loc, timeout)
        el.clear()
        el.send_keys(text)
        el.send_keys(Keys.ENTER)

    def click_button(self, btn, timeout=10):
        BaseClass.wait_clickable(self.driver, btn, timeout).click()

    def click_radio_button(self, rdo, timeout=10):
        BaseClass.wait_clickable(self.driver, rdo, timeout).click()

    def click_toggle(self, tgl, timeout=10):
        BaseClass.wait_clickable(self.driver, tgl, timeout).click()

    def click_listbox(self, lst, timeout=10):
        BaseClass.wait_clickable(self.driver, lst, timeout).click()

    def click_checkbox(self, chk, timeout=10):
        BaseClass.wait_clickable(self.driver, chk, timeout).click()

    def click_menu(self, menu, timeout=10):
        BaseClass.wait_clickable(self.driver, menu, timeout).click()

    def click_dropdown(self, drop, timeout=10):
        BaseClass.wait_clickable(self.driver, drop, timeout).click()

    def click_tab(self, tab, timeout=10):
        BaseClass.wait_clickable(self.driver, tab, timeout).click()

    def click_image(self, img, timeout=10):
        BaseClass.wait_clickable(self.driver, img, timeout).click()

    def scroll_to_top(self):
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)

    def get_text(self, loc, timeout=10):
        el = BaseClass.wait_visible(self.driver, loc, timeout)
        return el.get_attribute("value")
    
    def get_textContent(self, loc, timeout=10):
        el = BaseClass.wait_visible(self.driver, loc, timeout)
        return el.get_attribute("textContent")

    def open_new_tab(self, url):
        self.driver.execute_script(f"window.open('{url}');")
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def switch_tab(self, title):
        handles = self.driver.window_handles
    
        for handle in handles:
            self.driver.switch_to.window(handle)

            if title in self.driver.title:
                return True
            
        return False
    
    def get_current_url(self):
        url = self.driver.current_url
        return url
    
    def delete_campaign(self, driver):
        while True:
            try:
                time.sleep(1)
                el = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(self.test_campaign)
                )
                self.click_button(self.more_btn)
                self.click_button(self.delete_icon)
                self.click_button(self.delete_icon_confirm)

            except TimeoutException:
                break 
            except Exception as e:
                print(f"삭제 도중 오류 발생: {e}")
                break

    def move_storage(self, driver):
        while True:
            try:
                time.sleep(1)
                el = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(self.test_campaign)
                )
                self.click_button(self.more_btn)
                self.click_button(self.moveto_storage)

            except TimeoutException:
                break 
            except Exception as e:
                # 예상치 못한 에러 발생 시 출력 후 종료
                print(f"삭제 도중 오류 발생: {e}")
                break