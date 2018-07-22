#coding:utf-8

import tushare as ts
import datetime
import os
import time
import sqlite3
import requests


def ts(aword):
    data = {
        "i": aword,
        "from": "AUTO",
        "to": "AUTO",
        "smartresult": "dict",
        "client": "fanyideskweb",
        "doctype": "json",
        "version": "2.1",
        "keyfrom": "fanyi.web",
        "action": "FY_BY_REALTIME",
        "typoResult": "true"
    }

    url = "http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule"
    res = requests.post(url, data=data)
    js = res.json()
    rs = js['translateResult'][0][0]['tgt']
    return rs

'''
    主入口
'''

if __name__ == '__main__':
    da = open('base.txt',encoding='UTF-8')
    i=0
    print(ts('修改人'))

