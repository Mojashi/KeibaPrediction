import pandas as pd
import nkf
import requests
import time
import subprocess
import os
import util

def predPage(url):
    # options.binary_location = '/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary'
    ins = makeQuery(url)
    proc = subprocess.Popen(['./prod'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE)
    stdout_value, stderr_value = proc.communicate(ins.encode())
    print(stderr_value)
    print(stdout_value.decode())
if __name__ == '__main__':
    predPage(input())