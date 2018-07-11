
from celery import Celery,platforms

import requests
import time
import random
from lxml import etree
import smtplib
from email.mime.text import MIMEText
from urllib import parse,request
from datetime import datetime 
from redis import *
from kaoweitongapp.dama import YDMHttp
from kaoweitongapp.all_func import str_md5, only_num, address_chinese_english, judge, headers_all, deal_with_time, make_new_list,time2china_time
import re
import os
import django 
from django.conf import settings 



app = Celery('kaoweitongapp/tasks', broker='redis://localhost:6379/0')  
# celery不能root用户启动解决(C_FORCE_ROOT environment),加上这一行即可
platforms.C_FORCE_ROOT = True




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

    def sismember(self,key,value):
        key = key
        value = value
        return self.sr.sismember(key,value)
    def del_(self, key):
        key = key
        self.sr.delete(key)


def main2(openid, neea, neea_pwd):
    """
        功能：执行一个月份多个省份查询功能的逻辑
        参数：month：月份，address_list：省份列表，f_data：保存数据的文件
        返回：res：查询后的结果       
    """
    openid = openid
    neea = neea
    neea_pwd = neea_pwd
    tuoful = Tuoful(openid, neea, neea_pwd)
    status = tuoful.loginin()
    i = 0
    while status == "error":
        tuoful = Tuoful(openid, neea, neea_pwd)
        status = tuoful.loginin()
        i += 1
        if i>= 10:
            values = {}
            values["openid"] = openid
            values["neea"] = neea
            send_mail(str(values))
            return "no"


def send_post(values_dic):
    data=parse.urlencode(values_dic)
    url='http://wx.testdaily.cn/neea'
    req=request.Request(url,data.encode(encoding='utf-8'))
    res=request.urlopen(req)
    print(res.read())

    
def send_mail(res): # 将结果发送邮件

    msg_from='1298045658@qq.com'                                 
    passwd='lujdzcveprsyijce'                                   
    msg_to='sunzhangming@testdaily.cn'                     
    content = res                           
    subject="有新考位放出啦"                                
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

@app.task
def check_neea(openid,neea,neea_pwd):
	openid = openid
	neea = neea
	neea_pwd = neea_pwd
	main2(openid,neea,neea_pwd)

@app.task
def weixininfo(vcChatRoomSerialNo,vcNickName):
    redis_w = Redis()
    time.sleep(5)
    # with open("/www/wwwroot/kaoweitong_spider/weixinuserinfo.txt","r") as f:
    lines = redis_w.smembers("vcChatRoomSerialNo")
        # lines = f.readlines()
    temp_list = []
    for line in lines:
        # line = line.decode().replace("\n","")
        NickName = line.decode().split(",")[0]
        print(NickName)
        print(vcNickName)
        if vcNickName == NickName:
            vcSerialNo = line.decode().split(",")[1]
            # temp_dict[vcSerialNo] = "%s,%s,%s"%(vcChatRoomSerialNo,NickName,line.decode().split(",")[2])
            temp_dict = {"用户编号":vcSerialNo,"微信群编号":vcChatRoomSerialNo,"用户昵称":NickName,"头像地址":line.decode().split(",")[2]}
            temp_list.append(temp_dict)
    # send_mail(str(temp_list))
    send_user(str(temp_list))
    redis_w.del_("vcChatRoomSerialNo")

def send_user(values):
    values_dic = {}
    values_dic["1"] = values
    data=parse.urlencode(values_dic)
    url='http://wx.testdaily.cn/neea'
    req=request.Request(url,data.encode(encoding='utf-8'))
    res=request.urlopen(req)
    print(res.read())