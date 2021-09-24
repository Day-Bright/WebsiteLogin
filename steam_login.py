import requests
import time
import execjs
from datetime import datetime
import sys

sys.path.append("..")
import web_heardes.steam_heardes as heardes


def getRESpubKey(username):
    res_url = "https://store.steampowered.com/login/getrsakey/"
    username = username
    millis = int(round(time.time() * 1000))
    res_data = {
        "donotcache": millis,
        "username": username
    }
    response = requests.post(url=res_url, data=res_data, headers=heardes.res_heardes).json()
    publickey_mod = response["publickey_mod"]
    publickey_exp = response["publickey_exp"]
    timestamp = response["timestamp"]
    return publickey_mod, publickey_exp, timestamp


def getEncryptKey(username, password):
    getData = getRESpubKey(username)
    password = password
    file = "web_js/steam_login.js"
    ctx = execjs.compile(open(file, encoding="utf-8").read())
    js = 'getpwd("{password}","{publickey_mod}","{publickey_exp}")'.format(password=password, publickey_exp=getData[1],
                                                                           publickey_mod=getData[0])
    encrypt_key = ctx.eval(js)
    return username, encrypt_key, getData[2]


session = requests.Session()
GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
gmt_time = datetime.utcnow().strftime(GMT_FORMAT)
encryptkey = getEncryptKey("xxx", "xxx")  # 输入账号，密码
login_url = "https://store.steampowered.com/login/dologin/"
millis = int(round(time.time() * 1000))
login_data = {
    "donotcache": int(round(time.time() * 1000)),
    "password": encryptkey[1],
    "username": encryptkey[0],
    "twofactorcode": "",
    "emailauth": "",
    "loginfriendlyname": "",
    "captchagid": -1,
    "captcha_text": "",
    "emailsteamid": "",
    "rsatimestamp": encryptkey[2],
    "remember_login": "false",
}
login_response = session.post(url=login_url, data=login_data, headers=heardes.login_heardes)
main_url = "https://store.steampowered.com/"
main_response = session.get(url=main_url, headers=heardes.main_heardes)
with open("steam.html", "w", encoding="utf-8") as f:
    f.write(main_response.text)
