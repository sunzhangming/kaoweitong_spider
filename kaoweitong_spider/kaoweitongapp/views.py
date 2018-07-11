# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader,RequestContext
import requests
import json
import ast
import time
import random
import string
import base64
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
from .tasks import check_neea,weixininfo

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

    def rpush(self,key,value):
        key = key
        value = value
        return self.sr.rpush(key, value)

    def blpop(self,key):
        key = key
        self.sr.blpop(key,timeout=2)

    def lrange(self,key):
        key = key
        return self.sr.lrange(key,0,-1)
    def del_(self, key):
        key = key
        self.sr.delete(key)
    def srandmember(self,key):
        key = key
        return self.sr.srandmember(key)


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

# ==============================================================================       

def send_mail(res): # 将结果发送邮件

    msg_from='1298045658@qq.com'                                 
    passwd='lujdzcveprsyijce'                                   
    msg_to='sunzhangming@testdaily.cn'                                  
                                
    subject="有新考位放出啦"                                
    content=res
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
            send_post(values)
            return "no"
    return "ok"

def send_post(values_dic):
    data=parse.urlencode(values_dic)
    url='http://wx.testdaily.cn/neea'
    req=request.Request(url,data.encode(encoding='utf-8'))
    res=request.urlopen(req)
    print(res.read())

def join_get(vcRelaSerialNo, content, vcChatRoomSerialNo, msgtype, vcTitle, vcDesc, vcHref,nIsHit):
    STRCONTEXT={
        "MerchantNo": "201805021010006",
        "vcRelaSerialNo": "%s"%vcRelaSerialNo,
        "vcChatRoomSerialNo": "%s"%vcChatRoomSerialNo,
        "vcRobotSerialNo": "",
        "nIsHit": nIsHit,
        "vcWeixinSerialNo": "",
        "Data": [
            {   "nMsgNum":"1",
                "nCallBack":"0",
                "nMsgType": msgtype,
                "msgContent": "%s"%content,
                "vcTitle": vcTitle,
                "vcDesc": vcDesc,
                "nVoiceTime": "0",
                "vcHref": vcHref
            }]
                }
    return STRCONTEXT

def random_num():
    # 生成随机数字字符串
    num =''
    for _ in range(15):
        num += random.choice(string.digits)
    return num

def send_weixin(vcChatRoomSerialNo):
    # 发送群回调
    STRCONTEXT={
                "MerchantNo":"201805021010006",
                "vcChatRoomSerialNo":"%s"%vcChatRoomSerialNo
            }
    STRSIGN = str_md5(str(STRCONTEXT)+"testdaily123456") 
    content = requests.get("http://skyagent.shequnguanjia.com/Merchant.asmx/ChatRoomUserInfo?strContext=%s&strSign=%s"%(STRCONTEXT,STRSIGN))



# =======================================================================

def neea(request):
    if request.method == "POST":
        neea = request.POST.get("neea")
        neea_pwd = request.POST.get("neea_pwd")
        openid = request.POST.get("openid")
        print("正在检验账号密码是否正确")
        check_neea.delay(openid, neea, neea_pwd)

    return HttpResponse("正在检验账号密码是否正确")

def chengji(request):
    start_time = datetime.now()
    redis_ = Redis()
    if request.method == "POST":
        neea = request.POST.get("neea")
        neea_pwd = request.POST.get("neea_pwd")
        openid = request.POST.get("openid")
        test_date = request.POST.get("test_date")
        all_task = redis_.smembers("all_task")
        print(all_task)
        if not all_task:
            add_task = "%s,%s,%s,%s"%(neea, neea_pwd, test_date, openid)
            print(add_task)
            redis_.sadd("all_task",add_task)
        else:
            for task in all_task:
                if test_date not in task.decode():

                    add_task = "%s,%s,%s,%s"%(neea, neea_pwd, test_date, openid)
                    print(add_task)
                    redis_.sadd("all_task",add_task)

    end_time = datetime.now()
    print((end_time - start_time).seconds)
    return HttpResponse("ok")

def index(request):
    """
        功能：测试http://kw.testdaily.cn/是否可连接
        参数：request：自带的
        返回：测试结果
    """
    redis_ = Redis()
    res = redis_.srandmember("soul")
    now = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    template=loader.get_template('kaoweitongapp/soul.html')
    context=template.render({"res":res.decode("utf8"),"now":now})

    return HttpResponse(context)

def addindex(request):
    redis_ = Redis()
    if request.method == "POST":
        content = request.POST.get("content")
        redis_.sadd("soul",content)
    return HttpResponse("ok")

    
def kaowei(request):
    if request.method == "POST":
        month = request.POST.get("month")
        address = request.POST.get("address")
        neea = "8398103"
        neea_pwd = "198476zwJ_A"
        month_address = month+","+address
        redis_ = Redis()
        if not redis_.sismember("month_address",month_address):
            redis_.sadd("month_address",month_address)


        return HttpResponse("ok")


# ==============================================================================

def weixin(request):
    # 获取群成员回调信息
    if request.method == "POST":
        redis_ = Redis()
        strContext = request.POST.dict()["strContext"]
        data = ast.literal_eval(strContext)["Data"]
        print(strContext)
        data = data[0]["ChatRoomUserData"]
        vcChatRoomSerialNo = ast.literal_eval(strContext)["vcChatRoomSerialNo"]
        for i in data:
            userinfo = "%s,%s,%s"%(i["vcBase64NickName"],i["vcSerialNo"],i["vcHeadImages"])
            redis_.sadd(vcChatRoomSerialNo,userinfo)
        return HttpResponse("SUCCESS")

vcChatRoomSerialNo_math = ["41C08CECCAE65597389188D73B168C4E","4046657315994040F85DA357F33E4042","B03FF8EAEEFC063355EED5D2ADA564D4"]
vcChatRoomSerialNo_2018SAT = ["AF85244D8D6B9AA7FB91D95411B1ED3B","32992BA15FBAC664B7CF1B221C8A56AB","452095899A708007FC6E28ABB1F35C86","25B359CA9A959A0E812616D9136F1923","6DD24529CE5081198E92458F5044CDE2","41C08CECCAE65597389188D73B168C4E"]

# vcChatRoomSerialNo_2018SAT = ["FA86A90266577732245C6B2AF3467207","B03FF8EAEEFC063355EED5D2ADA564D4","41C08CECCAE65597389188D73B168C4E"]
vcChatRoomSerialNo_2018SAT2 = ["24E78D043EA7F81D9383CBDABF2E804E","BD6C0EAFDDD7F06DAB2A6E94F2B7BF22","41C08CECCAE65597389188D73B168C4E","AD738D20E0CD6C0D46E23734FEBA6DEB","DFB86AF1F53C86853F2C5C9D15765C79","BCB07B4B620B93A110E471BC3B38C54F"]
vcChatRoomSerialNo_tuofufufei = ["E2E5C18E4C728A8F79314FDF35B0AB7F","E29B0CF48CD5A4DDC3004E503BE3DFC5","BC388627926988C519C82BAD1DE2FF13","95EA631D36CDC110A186D29AF21A0DC4","D5579EEA93C9784CBBED5B33B60793A1","41C08CECCAE65597389188D73B168C4E"]
vcChatRoomSerialNo_damodianci = ["82B496D8FBF8A1762D1B3B7BC7928FD6","93B02E8F3979B4D64FBC14EBF77483BF","662454DDC848A95F44524225652376C1","E8B9883001978BCB20BC080D3614CD83","9B78FFB1CCE74FCB74103B37194DA225","2ECC386595F0EF313E9562F762EC404D","82A8CE3A2957B4230EDF0658F259C503","9405271B7860EA88C3044A943C2B6341","585CC9E2523E274BC8B35F81121743B0","9B07DDA4FC209CBCBFE0ACDBACEA20A4","BD675AEE3EAD31AB309FAD5F96A8EC28","41C08CECCAE65597389188D73B168C4E"]
vcChatRoomSerialNo_SATduidu = ["6B5B7CE043ACBDF2806B28BA83676DAA","D16511946326F7FAEB6477F5494141D9","BFE21D11AFAB0248F5E94BD0D5E8C2A8","E1A17EAB0DA0B274E5B1139F3F26AD45","7021F7DDA6BE9E500987AE11AF4B7963","41C08CECCAE65597389188D73B168C4E"]
vcChatRoomSerialNo_AP = ["122E94D622133D45B9EFE1BEBD0CCCC0","204CB4CF0AA5F1C5C144BD5D27F3EF77","463444F6D46B56134D133C7E7941F91F","56316F1DCD333074E0E7521F4E13C56E","81039D75B358686D1CE47F5076816335","8E74698EE5BC2D40E62DAA9D282E7258","A775AC7FF45A45C5D37B52850A1ECE10","AB3AED30CA67236CC1B4B5494C39F5D0","F06D6201D4B3CC7C00EBE455E35A0D0F","41C08CECCAE65597389188D73B168C4E"]
def robotmass(request):
    # 机器人发送群消息
    if request.method == "POST":
        msgtype = request.POST.get("msgtype")
        vcTitle = request.POST.get("vcTitle")
        vcDesc = request.POST.get("vcDesc")
        vcHref = request.POST.get("vcHref")
        nIsHit = request.POST.get("nIsHit")
        if not vcTitle:
            vcTitle = ""
            vcDesc = ""
            vcHref = ""
        if msgtype == "text":
            msgtype = "2001"
        elif msgtype == "href":
            msgtype = "2005"
        group = request.POST.get("group")
        content = request.POST.get("content")
        vcRelaSerialNo = random_num() # 随机流水号
        if group == "数学":
            print(content)
            for vcChatRoomSerialNo in vcChatRoomSerialNo_math:
                STRCONTEXT = join_get(vcRelaSerialNo, content, vcChatRoomSerialNo, msgtype, vcTitle, vcDesc, vcHref, nIsHit)
                STRSIGN = str_md5(json.dumps(STRCONTEXT)+"testdaily123456")
                d = {"STRCONTEXT":json.dumps(STRCONTEXT),"STRSIGN":STRSIGN }
                res = requests.post("http://skyagent.shequnguanjia.com/Merchant.asmx/MerchantSendMessages",data = d)
            return HttpResponse("ok")
        elif group == "1":
            # SAT
            for vcChatRoomSerialNo in vcChatRoomSerialNo_2018SAT:
                STRCONTEXT = join_get(vcRelaSerialNo, content, vcChatRoomSerialNo, msgtype, vcTitle, vcDesc, vcHref, nIsHit)
                STRSIGN = str_md5(json.dumps(STRCONTEXT)+"testdaily123456")
                d = {"STRCONTEXT":json.dumps(STRCONTEXT),"STRSIGN":STRSIGN }
                res = requests.post("http://skyagent.shequnguanjia.com/Merchant.asmx/MerchantSendMessages",data = d)
            return HttpResponse("ok")
        elif group == "2":
            # SAT2
            for vcChatRoomSerialNo in vcChatRoomSerialNo_2018SAT2:
                STRCONTEXT = join_get(vcRelaSerialNo, content, vcChatRoomSerialNo, msgtype, vcTitle, vcDesc, vcHref, nIsHit)
                STRSIGN = str_md5(json.dumps(STRCONTEXT)+"testdaily123456")
                d = {"STRCONTEXT":json.dumps(STRCONTEXT),"STRSIGN":STRSIGN }
                res = requests.post("http://skyagent.shequnguanjia.com/Merchant.asmx/MerchantSendMessages",data = d)
            return HttpResponse("ok")
        elif group == "托福付费":
            for vcChatRoomSerialNo in vcChatRoomSerialNo_tuofufufei:
                STRCONTEXT = join_get(vcRelaSerialNo, content, vcChatRoomSerialNo, msgtype, vcTitle, vcDesc, vcHref, nIsHit)
                STRSIGN = str_md5(json.dumps(STRCONTEXT)+"testdaily123456")
                d = {"STRCONTEXT":json.dumps(STRCONTEXT),"STRSIGN":STRSIGN }
                res = requests.post("http://skyagent.shequnguanjia.com/Merchant.asmx/MerchantSendMessages",data = d)
            return HttpResponse("ok")
        elif group == "大漠点词":
            for vcChatRoomSerialNo in vcChatRoomSerialNo_damodianci:
                STRCONTEXT = join_get(vcRelaSerialNo, content, vcChatRoomSerialNo, msgtype, vcTitle, vcDesc, vcHref, nIsHit)
                STRSIGN = str_md5(json.dumps(STRCONTEXT)+"testdaily123456")
                d = {"STRCONTEXT":json.dumps(STRCONTEXT),"STRSIGN":STRSIGN }
                res = requests.post("http://skyagent.shequnguanjia.com/Merchant.asmx/MerchantSendMessages",data = d)
            return HttpResponse("ok")
        elif group == "3":
            # SAT对赌
            for vcChatRoomSerialNo in vcChatRoomSerialNo_SATduidu:
                STRCONTEXT = join_get(vcRelaSerialNo, content, vcChatRoomSerialNo, msgtype, vcTitle, vcDesc, vcHref, nIsHit)
                STRSIGN = str_md5(json.dumps(STRCONTEXT)+"testdaily123456")
                d = {"STRCONTEXT":json.dumps(STRCONTEXT),"STRSIGN":STRSIGN }
                res = requests.post("http://skyagent.shequnguanjia.com/Merchant.asmx/MerchantSendMessages",data = d)
            return HttpResponse("ok")
        elif group == "AP":
            # AP
            for vcChatRoomSerialNo in vcChatRoomSerialNo_AP:
                STRCONTEXT = join_get(vcRelaSerialNo, content, vcChatRoomSerialNo, msgtype, vcTitle, vcDesc, vcHref, nIsHit)
                STRSIGN = str_md5(json.dumps(STRCONTEXT)+"testdaily123456")
                d = {"STRCONTEXT":json.dumps(STRCONTEXT),"STRSIGN":STRSIGN }
                res = requests.post("http://skyagent.shequnguanjia.com/Merchant.asmx/MerchantSendMessages",data = d)
            return HttpResponse("ok")


def kicking(request):
    if request.method == "POST":
        vcChatRoomSerialNo = request.POST.get("vcChatRoomSerialNo")
        vcSerialNo = request.POST.get("vcSerialNo")
        STRCONTEXT={
                    "MerchantNo":"201805021010006",
                    "Data":[
                                {
                                    "vcRelationSerialNo":"000000000002",
                                    "vcChatRoomSerialNo":"%s"%vcChatRoomSerialNo,
                                    "vcWxUserSerialNo":"%s"%vcSerialNo,
                                    "vcComment":""
                                }
                           ]
                }
        STRSIGN = str_md5(str(STRCONTEXT)+"testdaily123456") 
        content = requests.get("http://skyagent.shequnguanjia.com/Merchant.asmx/ChatRoomKicking?strContext=%s&strSign=%s"%(STRCONTEXT,STRSIGN))
        return HttpResponse(content.text)

def inmessage(request):
    # 获取群消息回调信息
    if request.method == "POST":
        redis_ = Redis()
        strContext = request.POST.dict()["strContext"]
        data = ast.literal_eval(strContext)["Data"]
        data = data[0]
        key = data["vcChatRoomSerialNo"] + data["vcChatRoomSerialNo"]
        num = redis_.rpush(key,data)
        if num > 10:
            temp = redis_.blpop(key)
        return HttpResponse("SUCCESS")

def groupinfo(request):
    # 查询群消息
    
    if request.method == "POST":
        redis_ = Redis()
        group = request.POST.get("group")
        if group == "实验群":
            vcChatRoomSerialNo = "FA86A90266577732245C6B2AF3467207"
        elif group == "实验群2":
            vcChatRoomSerialNo = "B03FF8EAEEFC063355EED5D2ADA564D4"
        key = vcChatRoomSerialNo+vcChatRoomSerialNo
        res_list = redis_.lrange(key)
        message_list = []
        for res in res_list:
            res = res.decode()
            res = eval(res)
            message_dict = {}
            message_dict["content"] = base64.b64decode(res["vcContent"]).decode().replace("\n","")
            message_dict["fayantime"] = res["dtMsgTime"]
            message_dict["fayanrenbianhao"] = res["vcFromWxUserSerialNo"]
            message_dict["qunbianhao"] = res["vcChatRoomSerialNo"]
            message_list.append(message_dict)
        # send_message_list(message_list)
        # send_mail(str(message_list))
        resp = {"a":message_list}
        return HttpResponse(json.dumps(resp,ensure_ascii=False), content_type="application/json")

def send_message_list(message_list):
    values={"-":message_list}
    data=parse.urlencode(values)
    url='http://wx.testdaily.cn/kaoweiinfo'
    req=request.Request(url,data.encode(encoding='utf-8'))
    res=request.urlopen(req)
    print(res.read())

def kick(request):
    # 机器人踢人查询
    if request.method == "POST":
        
        vcChatRoomSerialNo = request.POST.get("group")
        send_weixin(vcChatRoomSerialNo)
        return HttpResponse("ok")

def weixininfo(request):
    if request.method == "POST":
        redis_w = Redis()
        vcChatRoomSerialNo = request.POST.get("vcChatRoomSerialNo") 
        lines = redis_w.smembers(vcChatRoomSerialNo)
        temp_list = []
        for line in lines:
            vcSerialNo = line.decode().split(",")[1]
            temp_dict = {"yonghubianhao":vcSerialNo,"weixinqunbianhao":vcChatRoomSerialNo,"yonghunicheng":line.decode().split(",")[0],"touxiangdizhi":line.decode().split(",")[2]}
            temp_list.append(temp_dict)
        resp = {"a":temp_list}
        redis_w.del_(vcChatRoomSerialNo)
        return HttpResponse(json.dumps(resp,ensure_ascii=False), content_type="application/json")
        
def ktq(request):
    STRCONTEXT={
                 "MerchantNo":"201805021010006",
                 "vcRobotSerialNo":"159562E24C83A1131D41E7887CB4FCC8",
                 "nType":"10",
                 "vcChatRoomSerialNo":"",
                 "nCodeCount":"1",
                 "nAddMinute":"10",
                 "nIsNotify":"0",
                 "vcNotifyContent":""
             }
    STRSIGN = str_md5(str(STRCONTEXT)+"testdaily123456")
    content = requests.get("http://skyagent.shequnguanjia.com/Merchant.asmx/ApplyCodeList?strContext=%s&strSign=%s"%(STRCONTEXT,STRSIGN))
    res = content.text
    res = eval(res)
    res = res["Data"]
    res = res[0]
    res = res["ApplyCodeData"]
    res = res[0]
    res = res["vcCode"]
    template=loader.get_template('kaoweitongapp/yz.html')
    context=template.render({"yz":res})
    return HttpResponse(context)
