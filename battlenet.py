# -*- coding: UTF-8 -*-

"""
@Product ：VScode
@File    ：battlenet.py
@Date    ：2021/10/08 22:40:29
@Author  ：XYJ
@Contact ：1520207872@qq.com
"""


import requests
import web_heardes.battlenet_heardes as heardes
from bs4 import BeautifulSoup
import json


def inf(username):
    inf_url1 = "https://www.battlenet.com.cn/login/zh/"
    response = requests.get(url=inf_url1, headers=heardes.inf_heardes1)
    soup = BeautifulSoup(response.content, 'lxml', from_encoding='utf-8')
    csrftoken = soup.find('input', id='csrftoken')["value"]
    sessionTimeout = soup.find('input', id='sessionTimeout')["value"]
    # print(csrftoken, sessionTimeout)
    inf_url2 = "https://www.battlenet.com.cn/login/srp?csrfToken=true"
    data = {
        "inputs": [
            {
                "input_id": "account_name",
                "value": username
            }
        ]
    }
    response = requests.post(url=inf_url2, headers=heardes.inf_heardes2, data=json.dumps(data))
    inf_dict = json.loads(response.text)
    return csrftoken, sessionTimeout, inf_dict


if __name__ == '__main__':
    print(inf("1111@qq.com"))
