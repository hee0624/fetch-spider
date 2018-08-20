# encoding:utf-8

import time
import random
import io
from PIL import Image
from math import sqrt
from ims import ims
from selenium import webdriver
from selenium.webdriver.remote.command import Command
from selenium.webdriver.common.action_chains import ActionChains


PIXELS = []

def getExactly(im):
    """ 精确剪切"""
    imin = -1
    imax = -1
    jmin = -1
    jmax = -1
    row = im.size[0]
    col = im.size[1]
    for i in range(row):
        for j in range(col):
            if im.load()[i, j] != 255:
                imax = i
                break
        if imax == -1:
            imin = i

    for j in range(col):
        for i in range(row):
            if im.load()[i, j] != 255:
                jmax = j
                break
        if jmax == -1:
            jmin = j
    return (imin + 1, jmin + 1, imax + 1, jmax + 1)

def getType(browser):
    """ 识别图形路径 """
    ttype = ''
    time.sleep(3.5)
    im0 = Image.open(io.BytesIO(browser.get_screenshot_as_png()))
    try:
        box = browser.find_element_by_id('patternCaptchaHolder')
    except:
        return ttype
    im = im0.crop((int(box.location['x']) + 10, int(box.location['y']) + 100, int(box.location['x']) + box.size['width'] - 10, int(box.location['y']) + box.size['height'] - 10)).convert('L')
    newBox = getExactly(im)
    im = im.crop(newBox)
    width = im.size[0]
    height = im.size[1]
    for png in ims.keys():
        isGoingOn = True
        for i in range(width):
            for j in range(height):
                if ((im.load()[i, j] >= 245 and ims[png][i][j] < 245) or (im.load()[i, j] < 245 and ims[png][i][j] >= 245)) and abs(ims[png][i][j] - im.load()[i, j]) > 10: # 以245为临界值，大约245为空白，小于245为线条；两个像素之间的差大约10，是为了去除245边界上的误差
                    isGoingOn = False
                    break
            if isGoingOn is False:
                ttype = ''
                break
            else:
                ttype = png
        else:
            break
    px0_x = box.location['x'] + 40 + newBox[0]
    px1_y = box.location['y'] + 130 + newBox[1]
    PIXELS.append((px0_x, px1_y))
    PIXELS.append((px0_x + 100, px1_y))
    PIXELS.append((px0_x, px1_y + 100))
    PIXELS.append((px0_x + 100, px1_y + 100))
    return ttype


def move(browser, coordinate, coordinate0):
    """ 从坐标coordinate0，移动到坐标coordinate """
    time.sleep(0.05)
    length = sqrt((coordinate[0] - coordinate0[0]) ** 2 + (coordinate[1] - coordinate0[1]) ** 2)  # 两点直线距离
    if length < 4:  # 如果两点之间距离小于4px，直接划过去
        ActionChains(browser).move_by_offset(coordinate[0] - coordinate0[0], coordinate[1] - coordinate0[1]).perform()
        return
    else:  # 递归，不断向着终点滑动
        step = random.randint(3, 5)
        x = int(step * (coordinate[0] - coordinate0[0]) / length)  # 按比例
        y = int(step * (coordinate[1] - coordinate0[1]) / length)
        ActionChains(browser).move_by_offset(x, y).perform()
        move(browser, coordinate, (coordinate0[0] + x, coordinate0[1] + y))

def draw(browser, ttype):
    """ 滑动 """
    if len(ttype) == 4:
        px0 = PIXELS[int(ttype[0]) - 1]
        login = browser.find_element_by_id('loginAction')
        ActionChains(browser).move_to_element(login).move_by_offset(px0[0] - login.location['x'] - int(login.size['width'] / 2), px0[1] - login.location['y'] - int(login.size['height'] / 2)).perform()
        browser.execute(Command.MOUSE_DOWN, {})

        px1 = PIXELS[int(ttype[1]) - 1]
        move(browser, (px1[0], px1[1]), px0)

        px2 = PIXELS[int(ttype[2]) - 1]
        move(browser, (px2[0], px2[1]), px1)

        px3 = PIXELS[int(ttype[3]) - 1]
        move(browser, (px3[0], px3[1]), px2)
        browser.execute(Command.MOUSE_UP, {})

def get_cookies(browser):
    cookies_list = browser.get_cookies()
    cookies_dict = {}
    for cookie in cookies_list:
        cookies_dict[cookie['name']] = cookie['value']
    print(cookies_dict)
    cookies = [k + "=" + v for k, v in cookies_dict.items()]
    cookies = ';'.join(item for item in cookies)
    return cookies


def make_cookies(users_dict):
    cookies_lst = []
    browser = webdriver.Chrome('/home/hee/Desktop/github/fetch-spider/bin/chromedriver')
    # browser = webdriver.PhantomJS('/home/hee/Desktop/github/fetch-spider/bin/phatomjs/bin/phantomjs')
    browser.set_window_size(1050, 840)
    for user, passwd in users_dict.items():
        browser.get('https://passport.weibo.cn/signin/login?entry=mweibo&r=https://weibo.cn/')
        time.sleep(1)
        name = browser.find_element_by_id('loginName')
        psw = browser.find_element_by_id('loginPassword')
        login = browser.find_element_by_id('loginAction')
        name.send_keys(user)
        psw.send_keys(passwd)
        login.click()
        ttype = getType(browser)  # 识别图形路径
        draw(browser, ttype)  # 滑动破解
        time.sleep(1)
        cookies = get_cookies(browser)
        cookies_lst.append(cookies)
        print(cookies)
    time.sleep(5)
    browser.close()
    return cookies_lst

if __name__ == '__main__':

    users_dict = {
        '15600920758': 'chenhe1993',
        '791962385@qq.com': 'sina0624####',
        '14575782371': 'ja684623',
        '15874645844': 'ja684629',


    }
    make_cookies(users_dict)
