#!/usr/bin/env python3
# -*-coding: utf-8 -*-

''' python 模拟登陆知乎 '''

'''
Required
- requests (must)
- pillow (chosen)
'''

import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib
import re
import time
import os.path
try:
    from PIL import Image
except:
    pass

# 构造 Request headers
agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
headers = {
    'User-Agent': agent
}

# 使用登陆Cookie信息, 捕获cookie并在后续连接请求时继续使用，实现模拟登陆
session = requests.session()
session.cookies =cookielib.LWPCookieJar(filename='cookies')
try:
    session.cookies.load(ignore_discard=True)
except:
    print("Cookie未能加载")


def get_xsrf():
    '''_xsrf是一个动态变化的参数'''
    index_url = 'http://www.zhihu.com'
    # 获取登陆时需要的_xsrf
    index_page = session.get(index_url, headers=headers)
    html = index_page.text
    pattern = r'name="_xsrf" value="(.*?)"'
    # 这里的_xsrf 返回的是一个list
    _xsrf = re.findall(pattern, html)
    return _xsrf[0]

#获取验证码
def get_captcha():
    time_of_captcha = str(int(time.time()*1000))
    captcha_url = 'http://www.zhihu.com/captcha.gif?r=' + time_of_captcha + "&type=login"
    r = session.get(captcha_url, headers=headers)
    with open('captcha.jpg', 'wb') as f:
        f.write(r.content)
    # 使用pillow 的 Image 来显示验证码
    # 如果没有安装 pillow ，那么到源代码所在的目录找到验证码然后手动输入
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        print(u'请到 %s 目录找到captcha.jpg 手动输入' % os.path.abspath('captcha.jpg'))
    captcha = input('请您输入验证码\n>')
    return captcha

def isLogin():
    ''' 通过查看用户个人信息来判断是否已经登录 '''
    url = 'https://www.zhihu.com/settings/profile' # 如果已经登录，服务器会返回一个OK码 200
    login_code = session.get(url, allow_redirects=False).status_code
    if int(x=login_code) == 200:
        return True
    else:
        return False

def login(secret, account):
    ''' 通过输入的用户名判断是否为手机号 '''
    if re.match(r"^1\d{10}$", account):
        print("手机号登录 \n")
        post_url = 'http://www.zhihu.com/login/phone_num'
        postdata = {
            '_xsrf': get_xsrf(),
            'password': secret,
            'remember_me': 'true',
            'phone_num': account
        }
    else:
        print("邮箱登陆 \n")
        post_url = 'http://www.zhihu.com/login/email'
        postdata = {
            '_xsrf': get_xsrf(),
            'password': secret,
            'remember_me': 'true',
            'email': account
        }
    try:
        ''' 不需要验证码直接登陆成功的情况 '''
        login_page = session.post(post_url, data=postdata, headers=headers)
        login_code = login_page.text
        print(login_page.status)
        print(login_code)
    except:
        ''' 需要验证码后才能登陆的情况 '''
        postdata["captcha"] = get_captcha()
        login_page = session.post(post_url, data=postdata, headers=headers)
        login_code = eval(login_page.text)
        print(login_code['msg'])
    session.cookies.save()

try:
    input = raw_input
except:
    pass

if __name__ == '__main__':
    if isLogin():
        print("您已经登陆啦！！")
    else:
        account = input('请输入您的用户名> \n  ')
        secret = input('请输入您的密码> \n  ')
        login(secret, account)
