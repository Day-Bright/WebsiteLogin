# -*- coding: UTF-8 -*-

"""
@Project ：website_login 
@Product ：PyCharm
@File    ：weibo_login.py
@Date    ：2021/10/4 22:47 
@Author  ：XYJ
@Contact ：1520207872@qq.com
"""
import base64
import time
import re
import execjs
import requests
import web_heardes.weibo_heardes as heardes


def getPubKey(usrename):
    getPubKey_url = "https://login.sina.com.cn/sso/prelogin.php"
    millis_start = int(round(time.time() * 1000))
    su = base64.b64encode(usrename.encode("utf-8"))
    su = str(su)[2:-1]
    params = {
        "entry": "weibo",
        "callback": "sinaSSOController.preloginCallBack",
        "su": su,
        "rsakt": "mod",
        "checkpin": "1",
        "client": "ssologin.js(v1.4.19)",
        "_": millis_start
    }
    getPubKey_response = requests.get(url=getPubKey_url, params=params, headers=heardes.getPubKey_heardes).text
    pattern = 'sinaSSOController.preloginCallBack\((.*?)\)'
    ret = re.findall(pattern, getPubKey_response)[0]
    pubkey_dict = eval(ret)
    return su, pubkey_dict, millis_start


def getEncryptKey(password, login_inf):
    pubkey_dict = login_inf[1]
    file = "web_js/weibo_login.js"
    ctx = execjs.compile(open(file, encoding="utf-8").read())
    js = 'getpwd("{password}","{rsaPubkey}","{servertime}","{nonce}")'.format(password=password,
                                                                              rsaPubkey=pubkey_dict["pubkey"],
                                                                              servertime=pubkey_dict["servertime"],
                                                                              nonce=pubkey_dict["nonce"])
    encrypt_key = ctx.eval(js)
    return encrypt_key


def login(login_inf, encrypt_key):
    """
    返回结果中携带token 即登录成功
    :param login_inf:
    :param encrypt_key:
    :return:
    """
    pubkey_dict = login_inf[1]
    prelt = int(time.time() * 1000) - login_inf[2] - pubkey_dict['exectime']
    login_url = "https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)"
    data = {
        "entry": "weibo",
        "gateway": "1",
        "from": "",
        "savestate": "7",
        "qrcode_flag": "false",
        "useticket": "1",
        "pagerefer": "https://weibo.com/newlogin?tabtype=weibo&gid=102803&url=https%3A%2F%2Fweibo.com%2F",
        "vsnf": "1",
        "su": login_inf[0],
        "service": "miniblog",
        "servertime": pubkey_dict["servertime"],
        "nonce": pubkey_dict["nonce"],
        "pwencode": "rsa2",
        "rsakv": pubkey_dict["rsakv"],
        "sp": encrypt_key,
        "sr": "1536*864",
        "encoding": "UTF-8",
        "prelt": prelt,
        "url": "https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack",
        "returntype": "META",
    }
    response = requests.post(url=login_url, data=data, headers=heardes.login_heardes)
    return response


if __name__ == '__main__':
    login_inf = getPubKey("xxxxxx")
    encrypt_key = getEncryptKey("xxxxx", login_inf)
    response = login(login_inf, encrypt_key)
    print(response.text)
