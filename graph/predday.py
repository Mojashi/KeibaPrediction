import pandas as pd
import nkf
import bs4
import requests
import time
import subprocess
import os
import util
import nkf
import re

def predDay(day):
    url = "https://race.netkeiba.com/top/race_list_sub.html?kaisai_date=%s" % day

    print(url)
    body = nkf.nkf("-Ew",requests.get(url).content).decode()
    
    soup = bs4.BeautifulSoup(body, "html.parser")
    cou = 0
    ins = ""
    for item in soup.find_all(class_="RaceList_DataItem"):
        # print(item)
        if "Dart" in str(item):
            rid = re.findall(r"race_id=\d+",str(item))
            print(rid)
            cin = item.find("a").find("div").find("span").text + "\n"
            try:
                cin += (util.makeQuery("https://race.netkeiba.com/race/shutuba.html?%s" % rid[0]))
            except:
                continue
            else:
                ins += cin
                cou+=1
    ins = str(cou) + "\n" + ins
    proc = subprocess.Popen(['./prod'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE)
    stdout_value, stderr_value = proc.communicate(ins.encode())
    print(stderr_value)
    print(stdout_value.decode())
if __name__ == '__main__':
    predDay(input())
    util.quit()