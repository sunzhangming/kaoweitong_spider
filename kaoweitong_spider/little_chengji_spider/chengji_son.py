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
import pymysql
from redis import *
from dama import YDMHttp
from urllib import parse,request
from all_func import str_md5, only_num, address_chinese_english, make_new_list, headers_all,time2china_time,deal_with_time
import re
import os

class Mysql(object):
    def __init__(self):
        self.db = pymysql.connect("localhost","kaoweitong","3f5G7S3yWD6Ryip6","kaoweitong",charset="utf8" )

    def query_mysql(self,sql):
        # 使用cursor()方法获取操作游标 
        cursor = self.db.cursor()
         
        # SQL 插入语句
        sql = sql
        cursor.execute(sql)
        
        results = cursor.fetchall()

        return results

    def do_mysql(self,sql):
        # 使用cursor()方法获取操作游标 
        cursor = self.db.cursor()
         
        # SQL 插入语句
        sql = sql
        try:
           # 执行sql语句
           cursor.execute(sql)
           # 执行sql语句
           self.db.commit()

        except:
           # 发生错误时回滚
           self.db.rollback()


    def query_no_chengji(self,test_date):
        sql = "select * from spider_chengji where isFinished = 0 and test_date = '%s';"%(test_date)
        results = self.query_mysql(sql)
        if results:
            return results
        return results

    def query_all_no_chengji(self):
        sql = "select * from spider_chengji where isFinished = 0 ;"
        results = self.query_mysql(sql)
        if results:
            return results
        return results

    def remove_(self,values):
        # values_dic2 = {"openid":openid,"neea":neea}
        values = values
        sql = "delete from spider_chengji WHERE openid = '%s' and neea = '%s';"%(values["openid"], values["neea"])
        self.do_mysql(sql)



    def update_result(self, result, openid):
        now = str(time.time())
        sql="update spider_chengji set isFinished=1 , updated_time = '%s', reading = %d, listening = %d , speaking = %d, writing = %d  where openid = %s and test_date = '%s';" % (now, result["reading"], result["listening"], result["speaking"], result["writing"],openid,result["test_date"]) 
        self.do_mysql(sql)

                

    def send_post(self,now , timedate, city_str, status):
        values={"updated_time":now,"date":timedate,"city":city_str,"status":status}
        data=parse.urlencode(values)
        url='http://wx.testdaily.cn/kaoweiinfo'
        req=request.Request(url,data.encode(encoding='utf-8'))
        res=request.urlopen(req)
        print(res.read())

    def close(self):
        self.db.close()

class Tuoful(object):
    def __init__(self, mysql, neea, neea_pwd, test_date, openid):
        self.tuoful_session = requests.Session()
        self.Cookie_str = ' '
        self.neea = neea
        self.neea_pwd = neea_pwd
        self.test_date = test_date
        self.openid = openid
        self.mysql = mysql
        # self.conn = mysqlClient('140.143.193.71', 27017)
        # self.db = self.conn.kaoweitong_spider
        # self.my_set = self.db.test_set

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
        if "登录" not in text:
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
            headers_viewscores = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'zh-CN,zh;q=0.9',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'Cookie': self.Cookie_str,
            'Host':'toefl.etest.net.cn',
            'Referer': 'https://toefl.etest.net.cn/cn/MyHome/?',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            }
            headers_ScoreReport = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'zh-CN,zh;q=0.9',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'Cookie': self.Cookie_str,
            'Host':'toefl.etest.net.cn',
            'Referer': 'https://toefl.etest.net.cn/cn/ViewScores',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            }
            response = self.tuoful_session.get("https://toefl.etest.net.cn/cn/ViewScores", headers = headers_viewscores)
            text = response.content
            selector = etree.HTML(text)
            data = selector.xpath('//*[@id="maincontent"]//tr[2]/td[2]/text()')
            if len(data) != 0:
                if data[0] == self.test_date:
                    score_link = selector.xpath('//*[@id="maincontent"]//tr[2]/td[4]/a/@href')
                    score_links = "https://toefl.etest.net.cn%s"%score_link[0]
                    response = self.tuoful_session.get(score_links,headers = headers_ScoreReport)
                    text = response.content
                    selector = etree.HTML(text)
                    score_titles = selector.xpath('//*[@id="maincontent"]//tr[1]/td[@align="center"]/strong/text()')
                    score_title = score_titles[0:7]
                    score_res = selector.xpath('//*[@id="maincontent"]//tr[2]/td[@align="center"]/text()')
                    score_res = make_new_list(score_res[0:7])
                    # collection的名字：scoretasks
                    # 字段：openid，created，isFinished, test_date, neea, neea_pwd, isMatched, updated, result
                    # result是subCollection, reading, writing, listening, speaking
                    now = now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                    result = {"openid":"%s"%self.openid,"test_date":"%s"%deal_with_time(self.test_date),"result":{"reading":int(score_res[2]), "listening":int(score_res[3]), "speaking":int(score_res[4]), "writing":int(score_res[5])}}
                    print(result)
                    self.mysql.update_result(result, self.openid)
                    return result
                return "没有出分"
            return "没有出分"
                    
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


# //*[@id="maincontent"]/table/tbody/tr[2]/td[2]
def send_mail(staus):

    msg_from='1298045658@qq.com'                                 
    passwd='lujdzcveprsyijce'                                   
    msg_to='sunzhangming@testdaily.cn'                                  
                                
    subject="成绩放出了"                                
    content=staus
    print(content)
    msg = MIMEText(content)
    msg['Subject'] = subject
    msg['From'] = msg_from
    msg['To'] = msg_to
    try:
        s = smtplib.SMTP_SSL("smtp.qq.com",465)
        s.login(msg_from, passwd)
        s.sendmail(msg_from, msg_to, msg.as_string())
        print("发送成功")
    except s.SMTPException as e:
        print("发送失败")
    finally:
        s.quit()

def main2(mysql, openid, neea, neea_pwd, test_date):
    """
        功能：执行一个月份多个省份查询功能的逻辑
        参数：month：月份，address_list：省份列表，f_data：保存数据的文件
        返回：res：查询后的结果       
    """
    openid = openid
    neea = neea
    neea_pwd = neea_pwd
    test_date = test_date
    mysql = mysql
    redis_ = Redis()
    print(test_date)
    test_date = time2china_time(test_date)
    tuoful = Tuoful(mysql, neea, neea_pwd, test_date, openid)
    status = tuoful.loginin()
    i = 0
    while status == "error":
        tuoful = Tuoful(mysql, neea, neea_pwd, test_date, openid)
        status = tuoful.loginin()
        i += 1
        if i == 8:
            values_dic2 = {"openid":openid,"neea":neea}
            send_neea(values_dic2)
            mysql.remove_(values_dic2)
            all_task = redis_.smembers("all_task")
            for task in all_task:
                if openid in task.decode():
                    redis_.srem("all_task",task)

            return "error_no"
    if "没有出分" in status:
        return "no"
    else:
        # send_mail(status)
        # values_dic = {}
        # values_dic["出成绩了"]= status
        send_post(status)
        return "ok"
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

    def spop(self,key):
        key = key
        return self.sr.spop(key)
    def srem(self,key,value):
        key = key
        value = value
        self.sr.srem(key,value)

def send_post(dic):
    dic = dic
    data=parse.urlencode(dic)
    url='http://wx.testdaily.cn/scoreresult'
    req=request.Request(url,data.encode(encoding='utf-8'))
    res=request.urlopen(req)
    print(res.read())

def send_neea(values_dic):
    data=parse.urlencode(values_dic)
    url='http://wx.testdaily.cn/neea'
    req=request.Request(url,data.encode(encoding='utf-8'))
    res=request.urlopen(req)
    print(res.read())

def query(mysql, openid, neea, neea_pwd, test_date):
    neea = neea
    neea_pwd = neea_pwd
    openid = openid
    test_date = test_date
    mysql = mysql
    # test_date = time2china_time(test_date)
    main2(mysql, openid, neea, neea_pwd, test_date)


if __name__ == '__main__':
    redis_ = Redis()
    test_date = redis_.spop("task_son").decode()
    if test_date:
        mysql = Mysql()
        query_list = mysql.query_no_chengji(test_date)
        while query_list:
            for query_l in query_list:
                query(mysql, query_l[1], query_l[2], query_l[3],query_l[8])
            query_list = mysql.query_no_chengji(test_date)
            time.sleep(3600)
        mysql.close()
        all_task = redis_.smembers("all_task")
        for task in all_task:
            if task.decode().split(",")[2] == test_date:
                print(task.decode().split(",")[2],test_date)
                redis_.srem("all_task",task)

        

    

