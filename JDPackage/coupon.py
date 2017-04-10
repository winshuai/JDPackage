#encoding=utf-8
from selenium import webdriver
from rk import *
from PIL import ImageTk
from selenium.webdriver.common.keys import Keys
import time
import datetime
import sys
import re
import random
import os
import threading
import warnings
warnings.filterwarnings("ignore")
stdi,stdo,stde=sys.stdin,sys.stdout,sys.stderr
reload(sys)
sys.setdefaultencoding('utf-8',)
sys.stdin,sys.stdout,sys.stderr=stdi,stdo,stde
times=0
def login_check(html):
    if '图片验证码错误，请重试' in html:
        return False
    if '账号或密码不正确' in html:
        raise Exception('账号或密码不正确')
    return True
class Coupon:
    def __init__(self,username,pwd,rk_um,rk_pw):
        self.username=username
        self.pwd=pwd
        self.rc = RClient(rk_um, rk_pw)
        self.times=0
        self.ck=''
        if os.path.isdir('C:\Temp'):
            pass
        else:
            os.mkdir('C:\Temp')
    def login(self):
        rdname = str(random.randint(1000000, 10000000))
        driver = webdriver.PhantomJS()
        url = 'https://plogin.m.jd.com/user/login.action?appid=100&kpkey=&returnurl=http%3A%2F%2Fm.jd.com%3Findexloc%3D1%26sid%3D9129920d9c239d7273eed31ddcc2a0ab'
        driver.get(url)
        enabled=0
        while '专业网上购物平台品质保障' not in driver.title and enabled==0:
            driver.find_element_by_id("username").send_keys(self.username)
            driver.find_element_by_id("password").send_keys(self.pwd)
            driver.maximize_window()
            verify = False
            while verify == False:
                try:
                    driver.save_screenshot('C:\\temp\\'+rdname+'.jpg')
                    imgelement = driver.find_element_by_xpath('//*[@id="imgCode"]')
                    location = imgelement.location
                    size = imgelement.size
                    rangle = (
                        int(location['x']), int(location['y']),
                        int(location['x'] + size['width']),
                        int(location['y'] + size['height']))
                    frame4 = ImageTk.Image.open('C:\\temp\\'+rdname+'.jpg').crop(rangle)
                    frame4.save('C:\\temp\\'+rdname+'.png')
                    im = open('C:\\temp\\'+rdname+'.png','rb').read()
                    print '开始识别验证码',
                except:
                    raise Exception("请确认C:\Temp目录存在！")
                try:
                    codex = self.rc.rk_create(im, 3040)['Result']
                except Exception as err:
                    print err
                    raise Exception("若快验证码识别出错！")
                print codex
                print '->识别成功',
                driver.find_element_by_id("code").send_keys(codex)
                driver.find_element_by_xpath('//*[@id="loginBtn"]').send_keys(Keys.ENTER)
                print '->登陆中……',
                time.sleep(2)
                verify = login_check(driver.page_source)
                while 1 == 1 and verify == True and enabled == 0:
                    while '专业网上购物平台品质保障' in re.findall('<title>(.*?)</title>', driver.page_source, re.S)[
                        0] and enabled == 0:
                        #print '->请稍后……',
                        cookie = [item["name"] + "=" + item["value"] for item in driver.get_cookies()]
                        self.ck = ';'.join(item for item in cookie)
                        print self.username, '->登陆成功！'
                        enabled = 1
        driver.quit()
    def new_coupon(self,url_coupon,timex,endtime):
        url_filter='http://coupon.m.jd.com/coupons/show.action?key='+re.findall('key=(.*?)&',url_coupon,re.S)[0]+'&roleId='+re.findall('roleId=(.*?)&',url_coupon,re.S)[0]+'&to=m.jd.com'
        url_filter=str(url_filter)
        print url_filter
        timex = datetime.datetime.strptime(timex, '%Y-%m-%d %H:%M:%S')
        endtime = datetime.datetime.strptime(endtime, '%Y-%m-%d %H:%M:%S')
        enabled=0
        while enabled==0:
            if datetime.datetime.now() >= timex:
                threading.Thread(target=self.get_coupon, args=(url_filter,endtime,)).start()
                print 'Process Start'
                enabled=1
    def get_coupon(self,url,endtime):
        global times
        while datetime.datetime.now() <= endtime :
            if self.ck!='':
                rdname = str(random.randint(1000000, 10000000))
                headers = {'Cookie': self.ck, 'Referer': url}
                html = requests.get(url, headers=headers).text
                try:
                    ck = re.findall('authCodeImg.action\?key=(.*?)"', html, re.S)[0]
                    ir = requests.get("http://coupon.m.jd.com/authCode/authCodeImg.action?key=" + str(ck), headers=headers)
                    fp = open('C:\\temp\\'+rdname+'.png', 'wb')
                    fp.write(ir.content)
                    fp.close()
                    im = open('C:\\temp\\'+rdname+'.png', 'rb').read()
                    validatecode=self.rc.rk_create(im, 3040)['Result']
                except:
                    print '无需验证码，尝试直接领取'
                    validatecode=''
                    ck=''
                t1 = re.findall('id="codeKey"(.*?)id="validateCodeSign"', html, re.S)[0]
                datax = {'sid': re.findall('sid=(.*?)"', html, re.S)[0],
                         'codeKey': ck,
                         'validateCode': validatecode,
                         'roleId': re.findall('value="(.*?)"', t1, re.S)[0],
                         'key': re.findall('value="(.*?)"', t1, re.S)[1],
                         'couponKey': re.findall('value="(.*?)"', t1, re.S)[2],
                         'activeId': re.findall('value="(.*?)"', t1, re.S)[3],
                         'couponType': re.findall('value="(.*?)"', t1, re.S)[4],
                         'to': re.findall('value="(.*?)"', t1, re.S)[5]}
                now = requests.post('http://coupon.m.jd.com/coupons/submit.json', headers=headers, data=datax).text
                print re.findall('"returnMsg":"(.*?)"',now,re.S)[0],
                times=times+1
                print times
        print 'Times Up!Process End.'
if __name__=='__main__':
    t={}
    t[0] = Coupon('', '', '', '')
    t[0].login()
    t[0].new_coupon(
        'https://coupon.jd.com/ilink/couponActiveFront/front_index.action?key=61ea1f3fa9804499948617652d256485&roleId=6063883&to=mall.jd.com/index-13001.html',
        '2017-03-08 20:57:30','2017-04-08 00:11:40')
