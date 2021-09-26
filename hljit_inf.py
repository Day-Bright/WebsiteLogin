import execjs
import requests
import web_heardes.hljit_heardes as heardes
from bs4 import BeautifulSoup


# 获取登录信息
def getInf(password):
    session = requests.Session()
    hljit_url = "http://jw.hljit.edu.cn/"
    login_main = session.get(url=hljit_url, headers=heardes.hljit_heardes)
    cookie = session.cookies
    cookie = cookie.get_dict()
    # print(cookie)
    soup = BeautifulSoup(login_main.content, 'lxml', from_encoding='utf-8')
    viewstate = soup.find('input', id='__VIEWSTATE')["value"]
    viewstategenrator = soup.find('input', id='__VIEWSTATEGENERATOR')["value"]
    checkcode_src = soup.find('img', id='icode')["src"]
    txtKeyExponent = soup.find('input', id='txtKeyExponent')["value"]
    txtKeyModulus = soup.find('input', id='txtKeyModulus')["value"]
    file = "web_js/hljit_login.js"
    ctx = execjs.compile(open(file, encoding="utf-8").read())
    js = 'getpwd("{password}","{txtKeyExponent}","{txtKeyModulus}")'.format(password=password,
                                                                            txtKeyExponent=txtKeyExponent,
                                                                            txtKeyModulus=txtKeyModulus)
    encrypt_key = ctx.eval(js)
    checkcode_url = "http://jw.hljit.edu.cn" + checkcode_src
    checkcode_response = requests.get(url=checkcode_url, cookies=cookie, headers=heardes.checkcode_heardes).content
    with open(r"checkcode_img/checkcode.jpeg", "wb") as jpegFile:
        jpegFile.write(checkcode_response)

    # print("\n"+viewstate+"\n"+viewstategenrator+"\n"+txtKeyExponent+"\n"+txtKeyModulus+"\n"+encrypt_key)
    return cookie, viewstate, viewstategenrator, txtKeyExponent, txtKeyModulus, encrypt_key


# 登陆
def login(secretCode, userName, inf):
    cookie = inf[0]
    viewstate = inf[1]
    viewstategenrator = inf[2]
    txtKeyExponent = inf[3]
    txtKeyModulus = inf[4]
    encrypt_key = inf[5]
    login_url = "http://jw.hljit.edu.cn/default2.aspx"
    data = {
        "__LASTFOCUS": "",
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategenrator,
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "txtUserName": userName,  # 账号
        "TextBox2": encrypt_key,
        "txtSecretCode": secretCode,  # 验证码
        "RadioButtonList1": "学生",
        "Button1": "登录",
        "txtKeyExponent": txtKeyExponent,
        "txtKeyModulus": txtKeyModulus
    }
    login_response = requests.post(url=login_url, headers=heardes.hljit_heardes, data=data, cookies=cookie)
    main_url = "http://jw.hljit.edu.cn/xs_main.aspx?xh=20181092"
    main_response = requests.get(url=main_url, headers=heardes.main_heardes, cookies=cookie)
    with open("20181092.html", "w", encoding="utf-8") as f:
        f.write(main_response.text)


# 识别验证码
def checkcodeRecognition():
    pass


if __name__ == '__main__':
    inf = getInf("xxx")  # 输入密码
    checkcodeRecognition()  # 验证码识别未完成,完成可直接传入session,直接登录
    login("xxxx", "xxx", inf)  # 输入验证码，学号（验证码未自动识别）
