import pandas as pd
import nkf
import requests
import time
import subprocess
import os
from selenium import webdriver
import chromedriver_binary
from selenium.common.exceptions import NoSuchElementException        
from selenium.webdriver.chrome.options import Options

from selene.api import *

def predPage(url):
    # options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
    
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    LOGIN_ID="akihiro1001@gmail.com"
    PASSWORD="rA4Piyp23WWruYz"
    
    # 対象ページを開き、IDとPASSWORDをセットしてログイン（仮）
    driver.get("https://regist.netkeiba.com/account/?pid=login")
    driver.find_element_by_name("login_id").send_keys(LOGIN_ID)
    driver.find_element_by_name("pswd").send_keys(PASSWORD)
    
    driver.find_element_by_xpath("//*[@alt='ログイン']").click()

    driver.get(url)

    while True:
        try:
            elm = driver.find_element_by_id("odds_title")
        except NoSuchElementException:
            time.sleep(0.1)
        else:
            break
    print("found")
    body = driver.page_source
    html = pd.read_html(body)
    tb = html[0]
    
    ins = ""
    ins += str(len(tb)) + "\n"
    for row in tb.iterrows():
        print(row)
        oname = "予想オッズ"
        if "オッズ 更新" in tb.columns:
            oname = "オッズ 更新"
        if "オッズ" in tb.columns:
            oname = "オッズ"
        ins += "%s %s\n" % (row[1]["馬名"][0], row[1][oname][0])
    print(ins)
    proc = subprocess.Popen(['./prod'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE)
    stdout_value, stderr_value = proc.communicate(ins.encode())
    print(stderr_value)
    print(stdout_value.decode())
if __name__ == '__main__':
    predPage(input())