# -*- coding: utf-8 -*-
import requests
import json
import time
import random
import threading
import smtplib
from email.mime.text import MIMEText
from urllib import parse,request
from datetime import datetime 
import pymysql
from redis import *
from dama import YDMHttp
from all_func import str_md5, only_num, address_chinese_english, judge, headers_all, deal_with_time
import re
import os


# class Mysql(object):
#     def __init__(self):
#         self.db = pymysql.connect("localhost","kaoweitong","3f5G7S3yWD6Ryip6","kaoweitong",charset="utf8" )

#     def query_mysql(self,sql):
#         # 使用cursor()方法获取操作游标 
#         cursor = self.db.cursor()
         
#         # SQL 插入语句
#         sql = sql
#         cursor.execute(sql)
        
#         results = cursor.fetchall()

#         return results

#     def do_mysql(self,sql):
#         # 使用cursor()方法获取操作游标 
#         cursor = self.db.cursor()
         
#         # SQL 插入语句
#         sql = sql
#         try:
#            # 执行sql语句
#            cursor.execute(sql)
#            # 执行sql语句
#            self.db.commit()

#         except:
#            # 发生错误时回滚
#            self.db.rollback()

       
    
#     def deal_with_time_and_query_mysql(self, kaowei_list):
#         sql = "select * from spider_kaowei where city = '%s' and month = '%s';"%(kaowei_list[1], kaowei_list[0])
#         results = self.query_mysql(sql)
#         if results:
#             if results[0][5] != kaowei_list[2]:
#                 if results[0][5] == 1:
#                     now = str(time.time())
#                     sql="update spider_kaowei set status=0 , updated_time = '%s' where city = '%s' and month = '%s';" % (now,kaowei_list[1], kaowei_list[0] ) 
#                     self.do_mysql(sql)
#                 else:
#                     now = str(time.time())
#                     sql="update spider_kaowei set status=1 , updated_time = '%s' where city = '%s' and month = '%s';" % (now,kaowei_list[1], kaowei_list[0] )
#                     self.do_mysql(sql)
#                     res = "%s,%s有新考位放出!"%(kaowei_list[0], kaowei_list[1])
#                     print(res)
#                     self.send_mail(res)
#         else:
#             now = str(time.time())
#             sql = "insert into spider_kaowei(city, month, created_time,updated_time, status) VALUES('%s', '%s', '%s', '%s', '%d' );" % (kaowei_list[1], kaowei_list[0], now, now,kaowei_list[2] )
#             self.do_mysql(sql)

#     def send_post(self,timedate, city_str):
#         values={"date":timedate,"city":city_str}
#         data=parse.urlencode(values)
#         url='http://wx.testdaily.cn/kaoweiinfo'
#         req=request.Request(url,data.encode(encoding='utf-8'))
#         res=request.urlopen(req)
#         print(res.read())

    
#     def send_mail(self, res): # 将结果发送邮件

#         msg_from='1298045658@qq.com'                                 
#         passwd='lujdzcveprsyijce'                                   
#         msg_to='sunzhangming@testdaily.cn'                       
#         content = res                           
#         subject="有新考位放出啦"                                
#         msg = MIMEText(content)
#         msg['Subject'] = subject
#         msg['From'] = msg_from
#         msg['To'] = msg_to
#         try:
#             s = smtplib.SMTP_SSL("smtp.qq.com",465)
#             s.login(msg_from, passwd)
#             s.sendmail(msg_from, msg_to, msg.as_string())
#             print("发送成功")
#         except s.SMTPException as e:
#             print("发送失败")
#         finally:
#             s.quit()



#     def close(self):
#         self.db.close()



class Tuoful(object):
    def __init__(self, mysql, month, username, password):
        self.tuoful_session = requests.Session()
        self.Cookie_str = ' '
        self.month = month
        self.username = username
        self.password = password
        self.mysql = mysql
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
        # self.tuoful_session.proxies = {'http':"120.77.35.48:8899"}
        # content = self.tuoful_session.get("http://httpbin.org/ip")
        # print(content.text)
        response = self.tuoful_session.get("http://toefl.etest.net.cn/cn/")
        text = response.content.decode("gb2312")
        if "发生错误" in text:
            return "error"
        cook = response.cookies
        coo = {c.name: c.value for c in response.cookies}
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
        print("，打码平台识别验证码")
        num = only_num() #获取验证码内容
        codeContent = self.jpg2str(num, content_pic)
        headers_login = headers_all(self.Cookie_str)["headers_login"]
        s = str_md5("%s%s"%(self.password, self.username))
        x = s+codeContent
        pwd = str_md5(x)
        payload = {"username":"%s"%self.username,"__act":"__id.24.TOEFLAPP.appadp.actLogin","password":pwd,"LoginCode":codeContent,"btn_submit.x":"0","btn_submit.y":"0"}
        v = self.tuoful_session.post("https://toefl.etest.net.cn/cn/TOEFLAPP",data=payload, headers=headers_login)
        text = v.content.decode("gb2312")
        with open("e.html","w") as f:
            f.write(text)
        if "0; URL=/cn/MyHome/?" in text:
        # if True:
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

    def checkTest(self,address):
        """
            功能：进入选择和查询页面得到有考位的信息
            参数：address：要查询的省份地址
            返回：res：有考位的信息，error：查询失败     
        """
        headers_query = headers_all(self.Cookie_str)["headers_query"]
        response_query = self.tuoful_session.get("https://toefl.etest.net.cn/cn/Information?page=SeatsQuery",headers = headers_query)
        text = response_query.content.decode("gb2312")
        if "发生错误" in text:
            return "Access violation"
        #如果系统忙，休息1min后再次测试
        while self.checkBusy(text):
            print('系统繁忙,35s后再次测试')
            time.sleep(35)
            r = self.tuoful_session.get("https://toefl.etest.net.cn/cn/Information?page=SeatsQuery",headers = headers_query)
            text = str(r.content)
        #判断是否进入正常考试查询页面
        if text.find('省份') == -1:
            print('进入选择页面失败!')
            if "please relogin first" in text:
                print("please relogin first")
                return "please relogin first"
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
        headers_result = headers_all(self.Cookie_str)["headers_result"]
        url = "https://toefl.etest.net.cn/cn/SeatsQuery?"+"mvfAdminMonths=%s"%self.month+"&mvfSiteProvinces=%s"%address+"&whichFirst=AS"+"&afCalcResult="+str(codeContent)+"&__act=__id.22.SeatsQuery.adp.actList"+"&submit.x="+str(0)+"&submit.y="+str(0)
        r = self.tuoful_session.get(url, headers = headers_result)
        text = r.content.decode("gb2312")
        #如果系统忙，休息30后再次测试
        while self.checkBusy(text):
            print('系统繁忙,35s后再次测试')
            time.sleep(30)
            url = "https://toefl.etest.net.cn/cn/SeatsQuery?"+"mvfAdminMonths=%s"%self.month+"&mvfSiteProvinces=%s"%address+"&whichFirst=AS"+"&afCalcResult="+str(codeContent)+"&__act=__id.22.SeatsQuery.adp.actList"+"&submit.x="+str(0)+"&submit.y="+str(0)
            r = self.tuoful_session.get(url, headers = headers_result)
            text = r.content.decode("gb2312")
        #判断是否进入正常考试查询页面
        if text.find('考位查询结果') ==-1:
            print('进入查询页面失败!')
            if "Please login first" in text:
                print("Please login first")
                return "Please login first"
            elif ("请重新输入验证码" in text) or ("请输入验证码" in text):
                print("查询页面验证码错误")
                return "error_yz"
            else:
                print("发生未知错误 请查看kaowei.txt文件")
                with open("kaowei.txt","w") as f:
                    f.write(text)
            return "error"
        address = address
        pattern = '有名额'
        testList = re.findall(pattern,text,re.S)
        if len(testList)!=0:
            res = self.deal_with(text, address)
        else:
            res = self.deal_with(text,  address)
            print("%s%s没有考位"%(self.month, address))
        return res
    def deal_with(self, text, address):
        # time1 = re.findall(r'<tr bgcolor="#FFCC99">(.*?)</tr>', text, re.S)  # 匹配时间地区
        # if time1 != []:  # 匹配时间地区
        #     time_clear = re.findall(r'<b>(.*?)</b>', time1[0], re.S)     
        section_list = re.findall(r'(<tr.*?>.*?</tr>)',re.search(r'<table cellpadding="4" cellspacing="1">(.*?)</table>',text,re.S).group(),re.S)
        timedate = None
        aim_all = []
        dic = {}
        kaowei = {}
        for section in section_list[1:]:
            time_d = re.findall(r'<td.*?><b>(.*?)</b></td>',section,re.S)
            if time_d != []:
                timedate = deal_with_time(time_d[0])
                continue                    
            aim_list = re.findall(r'<tr bgcolor="#CCCCCC">(.*?)</tr>', section, re.S)
            for aim in aim_list:
                aim_clear = re.findall(r'<td.*?>(.*?)</td>', aim, re.S)
                if len(aim_clear) != 5:
                    print("偶尔发生数据紊乱，重新爬取此省")
                    return "error"
                aim_clear[0] = timedate
                aim_clear[1] = judge(aim_clear[1])
                if aim_clear[-1] == "有名额":
                    aim_clear[-1] = 1
                else:
                    aim_clear[-1] = 0
                del aim_clear[2:4]
                aim_clear[0] = aim_clear[0] + " " + aim_clear[1]
                del aim_clear[1]
                aim_all.append(aim_clear)
        for i in aim_all:
            if i[0] in dic:
                dic[i[0]] += i[1]
            else:
                dic[i[0]] = i[1]
        for k in dic.keys():
            kaowei_list = k.split(" ")
            if dic[k] > 0:
                
                kaowei_list.append(1)
            else:

                kaowei_list.append(0)
            print(kaowei_list)
            self.mysql.deal_with_time_and_query_mysql(kaowei_list)
                
                # ['2018-05-19', '北京',  1]
        print("%s考位查询完毕"%address)
        return "ok"
        



def main2(month, address, username, password):
    """
        功能：执行一个月份多个省份查询功能的逻辑
        参数：month：月份，address_list：省份列表，
        返回：res：查询后的结果       
    """
    month = month
    # mysql = Mysql()
    mysql = "d"
    tuoful = Tuoful(mysql, month, username, password)
    status = tuoful.loginin()
    i = 0
    while status == "error":
        i += 1
        if i >= 10:
            return "error"
        tuoful = Tuoful(mysql, month, username, password)
        status = tuoful.loginin()

    res = tuoful.checkTest(address)
    while res == "error_yz" :
        res = tuoful.checkTest(address)
    while (res == "please relogin first") or (res == "Please login first") or (res == "Access violation") or (res == "error"):
        tuoful = Tuoful(mysql, month, username, password)
        status = tuoful.loginin()
        while status == "error":
            tuoful = Tuoful(mysql, month, username, password)
            status = tuoful.loginin()
        res = tuoful.checkTest(address)
        while res == "error_yz":
            res = tuoful.checkTest(address)
        # if "没有考位" not in res:
        #     if len(res) != 0:

        #         send_mail(res)
        time.sleep(30)


class Redis(object):
    def __init__(self):
        self.sr = StrictRedis(host='localhost', port=6379, db=0)
    def sadd(self,key, value):
        key = key
        value = value
        self.sr.sadd(key,value)
    
    def smembers(self,key):
        key = key
        return self.sr.smembers(key)

def main():
    start_time = datetime.now()

    redis_ = Redis()
    month_address_set = redis_.smembers("month_address")
    for month_address in month_address_set:
        line_list = month_address.decode().split(",")
        test_data = line_list[0]
        address = line_list[1]


    # test_data = "201805"
    # address_list = ["Beijing", "Hebei", "Shanxi", "Tianjin", "Anhui","Fujian", "Jiangsu", "Jiangxi", "Shandong", "Shanghai", "Zhejiang", "Guangdong", "Guangxi", "Guizhou", "Hainan","Henan", "Hubei", "Hunan","Heilongjiang", "Jilin", "Liaoning", "Gansu", "Inner Mongolia", "Ningxia", "Qinghai", "Shaanxi", "Xinjiang", "Chongqing" ,"Sichuan", "Tibet", "Yunnan"]
    # # address_list = ["Jiangxi"]
        username = "1281490"
        password = "Zengyichao!123"
        err = main2(test_data, address, username, password)
        if err == "error":
            break
    end_time = datetime.now()
    print((end_time - start_time).seconds)


if __name__ == '__main__':
    while True:
        try:
            main()
            break
        except Exception as e:
            print(e)



        

    

