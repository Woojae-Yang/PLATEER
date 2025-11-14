
import time
import pytest
import sys 
import os 

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from PageObjects.dashboard import Dashboard
from TestData.LoginData import LoginData
from utilities.BaseClass import BaseClass


class SegmentPage:

    def __init__(self, driver):
        self.driver = driver

    #-------------------------element 선언 영역-------------------------
    ## 세그먼트 타게팅
    make_btn = (By.XPATH, '/html/body/div[4]/div[3]/div/div/div/div[2]/div/button')

    ### 새로운 세그먼트 만들기
    #### 세그먼트명
    seg_name_box = (By.XPATH, '/html/body/div[2]/div[3]/div/div/div/div[2]/div/div[1]/div/div[1]/div[2]/div/div/input')
    #### 상세 설명
    seg_dscr_box = (By.XPATH '/html/body/div[2]/div[3]/div/div/div/div[2]/div/div[1]/div/div[2]/div[2]/div/div/input')
    #### 기간 설정
    period_box = (By.XPATH, '/html/body/div[2]/div[3]/div/div/div/div[2]/div/div[2]/div/div[4]/div[2]/div/div/div[2]/div/input')
    #### 세그먼트 변수
    seg_var_btn = (By.XPATH, '/html/body/div[2]/div[3]/div/div/div/div[2]/div/div[3]/div/button')

    ##### 세그먼트 변수 RNB
    seg_var_rnb = (By.XPATH, '/html/body/div[3]/div[3]')
    ##### 시스템 요소
    rnb_system_elem = (By.XPATH, '/html/body/div[3]/div[3]/div[1]/div[3]/div[1]')
    ##### 브라우저 유형 요소
    rnb_browser_type = (By.XPATH, '/html/body/div[3]/div[3]/div[1]/div[3]/div[2]/div/div/div/div/ul/li[2]/div[1]/div')
    ##### 선택 버튼
    rnb_select_btn = (By.XPATH, '/html/body/div[3]/div[3]/div[2]/button')
    
    #### 과거 > 세그먼트 선택
    dropdown1 = (By.XPATH, '/html/body/div[2]/div[3]/div/div/div/div[2]/div/div[3]/div/div[2]/div[2]/div/div[2]/div[1]/div/div')
    dropdown2 = (By.XPATH, '/html/body/div[2]/div[3]/div/div/div/div[2]/div/div[3]/div/div[2]/div[2]/div/div[2]/div[2]/div/div')
    dropdown3 = (By.XPATH, '/html/body/div[2]/div[3]/div/div/div/div[2]/div/div[3]/div/div[2]/div[2]/div/div[2]/div[3]/div/div')


    #-------------------------동작 선언 영역-------------------------
    ## 만들기 버튼 클릭
    def enter_make_seg(self):
        self.driver.find_element(self.make_btn).click()
    ## 세그먼트 이름 입력
    def input_seg_name(self, today_date):
        seg_name = f'[Auto]segment{today_date}'
        input_box = self.driver.find_element(self.seg_name_box)
        input_box.click()
        input_box.clear()
        input_box.send_keys(seg_name)
    ### 세그먼트 변수 선택 RNB : 시스템 > 브라우저유형 > 선택
    def select_seg(self):
        self.driver.find_element(self.seg_var_btn).click()
        self.driver.find_element(self.rnb_system_elem).click()
        self.driver.find_element(self.rnb_browser_type).click()
        self.driver.find_element(self.rnb_select_btn).click()
    ## 세그먼트 변수 설정
    def set_seg_var(self):
        self.driver.find_element(self.dropdown1).click()
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//p[contains(text(),'브라우저 유형')]")
        self.driver.find_element(self.dropdown2).click()
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//p[contains(text(),'Chrome')]")
        self.driver.find_element(self.dropdown3).click()
        time.sleep(1)
        self.driver.find_element(By.XPATH, "//p[contains(text(),'일 때')]")


    #-------------------------동작 선언 영역-------------------------
    def create_segment(self, date : str):
        self.enter_make_seg()
        self.input_seg_name(date)
        self.select_seg()
        self.set_seg_var()
    
