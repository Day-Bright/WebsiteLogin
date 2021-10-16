import execjs
import requests
import web_heardes.hljit_heardes as heardes
from bs4 import BeautifulSoup
import urllib
import urllib.request
import base64
import muggle_ocr


def getInf(password):
    """
    获取登录相关信息
    :param password: 
    :return: 
    """
    session = requests.Session()
    hljit_url = "http://jw.hljit.edu.cn/"
    login_main = session.get(url=hljit_url, headers=heardes.hljit_heardes)
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
    checkcode_response = session.get(url=checkcode_url, headers=heardes.checkcode_heardes).content
    with open(r"checkcode_img/checkcode.jpeg", "wb") as jpegFile:
        jpegFile.write(checkcode_response)

    return session, viewstate, viewstategenrator, txtKeyExponent, txtKeyModulus, encrypt_key


def login(secretCode, userName, inf):
    """
    登录
    :param secretCode: 
    :param userName: 
    :param inf: 
    :return: 
    """
    session = inf[0]
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
    login_response = session.post(url=login_url, headers=heardes.hljit_heardes, data=data)
    print(login_response.status_code)
    main_url = "http://jw.hljit.edu.cn/xs_main.aspx?xh={userName}".format(userName=userName)
    main_response = session.get(url=main_url, headers=heardes.main_heardes)
    with open("20181092.html", "w", encoding="utf-8") as f:
        f.write(main_response.text)


def checkcodeRecognition():
    """
    api验证码识别
    :return: 
    """
    host = 'https://codevirify.market.alicloudapi.com'
    path = '/icredit_ai_image/verify_code/v1'
    appcode = '1991317cc15c4fdeaea568e29beace60'
    url = host + path
    bodys = {}
    querys = ""
    f = open(r'checkcode_img/checkcode.jpeg', 'rb')
    contents = base64.b64encode(f.read())
    f.close()
    bodys['IMAGE'] = contents
    bodys['IMAGE_TYPE'] = '0'
    post_data = urllib.parse.urlencode(bodys).encode('utf-8')
    request = urllib.request.Request(url, post_data)
    request.add_header('Authorization', 'APPCODE ' + appcode)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
    response = urllib.request.urlopen(request)
    content = response.read()
    if (content):
        checkcode = content.decode('utf-8')[-7:-3]
        print(checkcode)
        return checkcode


def checkcode_ocr():
    """
    muggle_ocr本地验证码识别
    :return: 
    """
    sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.Captcha)
    with open(r"checkcode_img/checkcode.jpeg", "rb") as f:
        b = f.read()
    checkcode = sdk.predict(image_bytes=b, param_key=4)
    print(checkcode)
    return checkcode


if __name__ == '__main__':
    inf = getInf("Hit911922")  # 输入密码
    # secretCode = checkcodeRecognition()  # 调用api
    secretCode = checkcode_ocr()
    login(secretCode, "20181092", inf)  # 输入验证码，学号
