import requests
import nkf
import time
import os
from selene.browsers import BrowserName
from selene.api import *

LOGIN_ID="akihiro1001@gmail.com"
PASSWORD="rA4Piyp23WWruYz"

config.browser_name = BrowserName.CHROME
# 対象ページを開き、IDとPASSWORDをセットしてログイン（仮）
browser.open_url("https://regist.netkeiba.com/account/?pid=login")
s('input[name="login_id"').set(LOGIN_ID)
s('input[name="pswd"').set(PASSWORD)
s('input[alt="ログイン"').click()
# Cookieを取得
cookies = browser.driver().get_cookies()
# 取得したCookieをrequestsに渡す形に変換
d = {}
for cookie in cookies:
    d[cookie["name"] ] = cookie["value"]

path = "./pages/"
ldir = sorted(os.listdir("pages"))
if len(ldir) > 1:
    os.remove("pages/" + ldir[-1])
ldir = sorted(os.listdir("pages"))
headers = {
    'User-Agent': 'Mozilla/5.0 xxxx'
}
def get_page(url, title):
    if title + ".html" in ldir:
        return True

    while True:
        time.sleep(0.5)
        # req = urllib.request.Request(url, cookies=d)
        print(url)
        try:
            body = nkf.nkf("-Ew",requests.get(url,headers=headers, cookies=d).content).decode()
            # print(body)
            # body = res.read().decode("euc-jp")
            if body.find("着") == -1:
                print("not chaku")
                return False
            with open(path + title + ".html", mode='w') as f:
                f.write(body)
            return True
        except Exception as err:
            time.sleep(10)
            print(err)
            pass
    return True

print("started")

base_url = 'https://db.netkeiba.com/race/'
#ex https://db.netkeiba.com/race/202005021201/

kuri = False

for year in range(2020,2021):
    for place in range(1,11):
        for kai in range(1, 6):
            for day in range(1, 13):
                for r in range(1, 13):
                    kuri = True
                    sign = (
                        str(year).zfill(2)
                        + str(place).zfill(2)
                        + str(kai).zfill(2)
                        + str(day).zfill(2)
                        + str(r).zfill(2)
                    )
                    url = base_url + sign
                    res = get_page(url+"/", sign)
                    if res is False and r == 1:
                        kuri = False
                        break
                if kuri is False and day == 1:
                    break
                elif kuri is False:
                    kuri = True
                    break
            if kuri is False and kai == 1:
                break
            elif kuri is False:
                kuri = True
                break
        # if kuri is False and place == 1:
        #     break
        # elif kuri is False:
        #     kuri = True
        #     break

print("complete")