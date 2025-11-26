# -*- coding: utf-8 -*-
"""
@author: WoojaeYang
"""


from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager # Chrome driver 자동 업데이트
from selenium.webdriver.support.ui import WebDriverWait


def create_driver():

    options = Options()
    
    # headless 옵션 설정
    # options.add_argument('--headless=new')
    options.add_argument("no-sandbox")
    
    # 브라우저 윈도우 사이즈
    #options.add_argument('--window-size=2560,2000')
    
    # 불필요한 에러메시지 노출 방지
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    # 사람처럼 보이게 하는 옵션들
    options.add_argument("disable-gpu")   # 가속 사용 x
    options.add_argument("lang=ko_KR")    # 가짜 플러그인 탑재
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')  # user-agent 이름 설정
    
    options.add_argument("start-maximized")
    options.add_argument("enable-automation")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")
    ##### 

    # 크롬드라이버 자동 업데이트
    service = Service(executable_path=ChromeDriverManager().install())
    
    # 드라이버 위치 경로 입력
    driver = webdriver.Chrome(service = service, options = options)
    driver.maximize_window()
    #driver.set_window_size(2560, 2000)

    wait = WebDriverWait(driver, 15)
    
    return driver, wait