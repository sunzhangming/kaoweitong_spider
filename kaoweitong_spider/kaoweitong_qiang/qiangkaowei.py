# -*- coding: utf-8 -*-
import requests
import json
import time
import random
import threading
import smtplib
from lxml import etree
from email.mime.text import MIMEText
from datetime import datetime 
from pymongo import MongoClient
from redis import *
from dama import YDMHttp
from urllib import parse,request
from all_func import str_md5, only_num, address_chinese_english, make_new_list, headers_all,time2china_time,deal_with_time,judge
import re
import os

class Tuoful(object):

    def __init__(self, openid, neea, neea_pwd):
        self.tuoful_session = requests.Session()
        self.Cookie_str = ' '
        self.neea = neea
        self.neea_pwd = neea_pwd
        self.openid = openid

    def jpg2str(self, num, content_pic):
        """
            功能：提交到打码平台，把验证码转换到string
            参数：图片链接
            返回：识别后的验证码       
        """
        
        file_name = "%s.jpg"%num
        f = open(file_name,'wb')
        f.write(content_pic.content)
        f.close()
        codeContent = YDMHttp().start(file_name)  # 云打码
        os.system("rm -rf %s"%file_name)
        return codeContent

    def checkBusy(self, text):
        """
            功能：判断网站是否忙碌
            参数：页面源码
            返回：True：安全，False：操作频繁       
        """
        if text.find('操作太频繁') == -1:
            return False
        else:
            return True

    
    def loginin(self):
        """
            功能：登录托福网站
            参数：None
            返回：ok：登陆成功，error：登录失败       
        """
        self.tuoful_session.cookies.clear()
        response = self.tuoful_session.get("http://toefl.etest.net.cn/cn/")
        text = response.content.decode("gb2312")
        # print(text)
        # if "登录" not in text:
        #     return "error"
        cook = response.cookies
        print(cook)
        coo = {c.name: c.value for c in response.cookies}
        print(coo)
        if "yunsuo_session_verify" in coo:
            return "error"
        else:
            temp_list = []
            for key,value in coo.items():
                srt = "%s=%s"%(key,value)
                temp_list.append(srt)
            self.Cookie_str = ";".join(temp_list)
        header_yz_login = headers_all(self.Cookie_str)["header_yz_login"]
        picUrl = "https://toefl.etest.net.cn/cn/"+ str(int(time.time()*1000))+str(random.random())[1:]+"VerifyCode3.jpg"
        content_pic = self.tuoful_session.get(picUrl,headers = header_yz_login)
        num = only_num()
        #获取验证码内容
        codeContent = self.jpg2str(num, content_pic)
        headers_login = headers_all(self.Cookie_str)["headers_login"]
        s = str_md5("%s%s"%(self.neea_pwd, self.neea))
        x = s+codeContent
        pwd = str_md5(x)
        payload = {"username":"%s"%self.neea,"__act":"__id.24.TOEFLAPP.appadp.actLogin","password":pwd,"LoginCode":codeContent,"btn_submit.x":"0","btn_submit.y":"0"}
        v = self.tuoful_session.post("https://toefl.etest.net.cn/cn/TOEFLAPP",data=payload, headers=headers_login)
        text = v.content.decode("gb2312")
        if "0; URL=/cn/MyHome/?" in text:
            return "ok"
                    
        elif "验证码错误" in text:
            now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            print("%slogin验证码错误"%(now))
            return "error"
        elif "密码不正确" in text:
            now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            print("%s密码不正确或验证码获取有误"%(now))
            return "error"
        else:
            print("发生未知错误 请查看login_error.txt文件")
            with open("login_error.txt", "w") as f:
                f.write(text)
            return "error"

    def check_balances(self):
        # https://toefl.etest.net.cn/cn/MyHome/
        headers_myhome = headers_all(self.Cookie_str)["headers_myhome"]
        response = self.tuoful_session.get("https://toefl.etest.net.cn/cn/MyHome/",headers = headers_myhome)
        text = response.content
        selector = etree.HTML(text)
        data = selector.xpath('//*[@id="rightside"]//tr[1]/td[2]/text()')
        money = data[0].split(" ")[1]
        if int(money) >= 1761:
            return "money is enough"
        else:
            return "money is not enough"

    def admintable(self):
        headers_admintable = headers_all(self.Cookie_str)["headers_admintable"]
        response_query = self.tuoful_session.get("https://toefl.etest.net.cn/cn/CityAdminTable",headers = headers_admintable)
        text = response_query.content.decode("gb2312")
        if "发生错误" in text:
            return "Access violation"
        #如果系统忙，休息1min后再次测试
        while self.checkBusy(text):
            print('系统繁忙,35s后再次测试')
            time.sleep(35)
            r = self.tuoful_session.get("https://toefl.etest.net.cn/cn/CityAdminTable",headers = headers_admintable)
            text = str(r.content)
        #判断是否进入正常考试查询页面
        if text.find('省份') == -1:
            print('进入选择页面失败!')
            if "please relogin first" in text:
                print("please relogin first")
                return "please relogin first"
            elif "注册并付费" in text:
                return "ok"
            else:
                print("发生未知错误 请查看information.html文件")
                with open("information.html","w") as f:
                    f.write(text)
                return "error"
        #获取验证码地址
        pattern1 = '<img src="/cn/'
        pattern2 = 'VerifyCode2.jpg'
        pos1 = text.find(pattern1)
        pos2 = text.find(pattern2)
        picUrl = 'https://toefl.etest.net.cn/'+text[pos1+11:pos2]+'VerifyCode2.jpg'
        num = only_num()
        content_pic = self.tuoful_session.get(picUrl) #获取验证码内容
        codeContent = self.jpg2str(num, content_pic)
        return codeContent
    def seatsquery(self, month, address, codeContent):
        headers_seatsquery = headers_all(self.Cookie_str)["headers_seatsquery"]
        url = "https://toefl.etest.net.cn/cn/SeatsQuery?mvfAdminMonths=%s&mvfSiteProvinces=%s&whichFirst=AS&afCalcResult=%s&__act=__id.34.AdminsSelected.adp.actListSelected&submit.x=0&submit.y=0"%(month, address, codeContent)
        # print(len(url))
        response_query = self.tuoful_session.get(url ,headers = headers_seatsquery)
        text = response_query.content.decode("gb2312")
        print(text)
        return text,url
    def get_para(self, text):
        text = text
        section_list = re.findall(r'(<tr.*?>.*?</tr>)',re.search(r'<table cellpadding="4" cellspacing="1">(.*?)</table>',text,re.S).group(),re.S)
        timedate = None
        aim_all = []
        dic = {}
        kaowei = {}
        for section in section_list[1:]:
            time_d = re.findall(r'<td.*?><b>(.*?)</b></td>',section,re.S)
            if time_d != []:
                timedate = deal_with_time(time_d[0]) + " " + time_d[0].split(" ")[1]
                continue                    
            aim_list = re.findall(r'<tr bgcolor="#CCCCCC">(.*?)</tr>', section, re.S)
            for aim in aim_list:
                aim_clear = re.findall(r'<td.*?>(.*?)</td>', aim, re.S)
                if len(aim_clear) != 6:
                    print("偶尔发生数据紊乱，重新爬取此省")
                    return "error"
                aim_clear[0] = timedate
                aim_clear[1] = judge(aim_clear[1])
                if aim_clear[-2] == "有名额":
                    if aim_clear[1] == "北京":
                        aim_clear[-2] = 1

                        # del aim_clear[2:4]
                        aim_clear[0] = aim_clear[0]
                        zhuce = aim_clear[-1].split(" ")
                        siteadmin = re.findall(r'value="(.*?)">',zhuce[3],re.S)[0]
                        aim_clear[-1] = siteadmin
                        __act = re.findall(r"onClick=.*?value='(.*?)';return",zhuce[17],re.S)[0]
                        aim_clear.append((__act))
                        aim_all.append(aim_clear)
        return aim_all

    def seatquery2(self,aim_all,url):
        headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Length':'129',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': self.Cookie_str,
        'Origin': 'https://toefl.etest.net.cn',
        'Host': 'toefl.etest.net.cn',
        'Referer': '%s'%url,
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        }
        __act = aim_all[0][-1]
        siteadmin = aim_all[0][-2]
        data = {'__act':__act,'siteadmin':siteadmin,'Submit':'%D7%A2%B2%E1'}
        content = self.tuoful_session.post(url = url, data = data, headers = headers)
        # print(content.content.decode("gb2312"))
        return "ok"

    def CityAdmin(self):
        headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'Referer':'https://toefl.etest.net.cn/cn/CityAdminTable',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Connection':'keep-alive',
        'Cookie':self.Cookie_str,
        'Host':'toefl.etest.net.cn',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36'
        }
        url = 'https://toefl.etest.net.cn/cn/?__id=CityAdminTable.dsa.actRegHold'
        content = self.tuoful_session.get(url = url, headers = headers)
        # print(content.content.decode('gb2312'))

    def ScoreRcpts(self):
        headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'Referer':'https://toefl.etest.net.cn/cn/?__id=CityAdminTable.dsa.actRegHold',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Connection':'keep-alive',
        'Cookie':self.Cookie_str,
        'Host':'toefl.etest.net.cn',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36'
        }
        url = 'https://toefl.etest.net.cn/cn/ScoreRcpts'
        content = self.tuoful_session.get(url = url, headers = headers)
        # print(content.content.decode('gb2312'))
    def scorercpts(self):
        headers = {
        'Referer':'https://toefl.etest.net.cn/cn/ScoreRcpts',
        'Cookie':self.Cookie_str,
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36'
        }
        url ='https://toefl.etest.net.cn/cn/ScoreRcpts?afDICode1=&afSchoolType1=&afDepartment1=&afDICode2=&afSchoolType2=&afDepartment2=&afDICode3=&afSchoolType3=&afDepartment3=&afDICode4=&afSchoolType4=&afDepartment4=&__act=__id.22.ScoreRcpts.adp.actPost&submit.x=10&submit.y=11'
        content = self.tuoful_session.get(url = url,headers = headers)
        # print(content.content.decode("gb2312"))
        return url

    def DmgrphQuestion(self,url2):
        headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'Referer':url2,
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Connection':'keep-alive',
        'Cookie':self.Cookie_str,
        'Host':'toefl.etest.net.cn',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36'
        }
        url = 'https://toefl.etest.net.cn/cn/DmgrphQuestion'
        content = self.tuoful_session.get(url = url,headers = headers)
        # print(content.content.decode("gb2312"))

    def DmgrphQuestion2(self):
        headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, br',
        'Referer':'https://toefl.etest.net.cn/cn/DmgrphQuestion',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Connection':'keep-alive',
        'Origin':'https://toefl.etest.net.cn',
        'Cookie':self.Cookie_str,
        'Host':'toefl.etest.net.cn',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36'
        }
        url = 'https://toefl.etest.net.cn/cn/DmgrphQuestion'
        data = {
        'ORGID':'0',
        'DQResponse24':'352',
        'DQResponse26':'',
        'DQResponse25':'291',
        'DQResponse14':'',
        'DQResponse27':'',
        'DQResponse28':'',
        '__act':'__id.26.DmgrphQuestion.adp.actPost',
        'btn_submit.x':'22',
        'btn_submit.y':'2',}
        content = self.tuoful_session.post(url = url, data = data, headers = headers)
        print(content.content.decode("gb2312"))



def main():
    openid = "test1"
    neea = "1281490"
    neea_pwd = "Zengyichao!123"
    month = "201812"
    address = "Beijing"
    tuoful = Tuoful(openid, neea, neea_pwd)
    status = tuoful.loginin()
    while status == "error":
        tuoful = Tuoful(openid, neea, neea_pwd)
        status = tuoful.loginin()
    res = tuoful.check_balances()
    if res == "money is enough":
        codeContent = tuoful.admintable()
        if codeContent != "ok":
            text,url  = tuoful.seatsquery(month, address, codeContent)
            aim_all = tuoful.get_para(text)
            tuoful.seatquery2(aim_all, url)
            tuoful.CityAdmin()
            tuoful.ScoreRcpts()
            url2 = tuoful.scorercpts()
            tuoful.DmgrphQuestion(url2)
            tuoful.DmgrphQuestion2()
        else:
            tuoful.CityAdmin()
            tuoful.ScoreRcpts()
            url2 = tuoful.scorercpts()
            tuoful.DmgrphQuestion(url2)
            tuoful.DmgrphQuestion2()


    else:
        pass




if __name__ == '__main__':
    main()

