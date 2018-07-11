# -*- coding: utf-8 -*-
import hashlib   
import time
import random
import string
import requests
import json

def str_md5(a): # 将字符串md5加密
    m2 = hashlib.md5()   
    m2.update(a.encode("utf8"))   
    return m2.hexdigest()  

def only_num(): # 生成随机字符串
    num =''
    for _ in range(15):
        num += random.choice(string.ascii_letters + string.digits)
    return num
    
def make_new_list(li): # 对列表的每一项操作
    new_list = []
    # 对原列表进行遍历  
    while li:  
        # 对每一个列表元素进行出栈操作，并在前面添加字符串，并保存在当前变量中  
        current_element = li.pop(0).replace("\n", "").strip()
        # 把当前变量保存在新列表中  
        new_list.append(current_element)  
          
    return new_list # 返回新列表  

def address_chinese_english(china_str): # 地名汉译英
    
    if china_str == "北京":
        return "Beijing"
    elif china_str == "河北":
        return "Hebei"
    elif china_str == "山西":
        return "Shanxi"
    elif china_str == "天津":
        return "Tianjin"
    elif china_str == "安徽":
        return "Anhui"
    elif china_str == "福建":
        return "Fujian"
    elif china_str == "江苏":
        return "Jiangsu"
    elif china_str == "江西":
        return "Jiangxi"
    elif china_str == "山东":
        return "Shandong"
    elif china_str == "上海":
        return "Shanghai"
    elif china_str == "浙江":
        return "Zhejiang"
    elif china_str == "广东":
        return "Guangdong"
    elif china_str == "广西":
        return "Guangxi"
    elif china_str == "贵州":
        return "Guizhou"
    elif china_str == "海南":
        return "Hainan"
    elif china_str == "河南":
        return "Henan"
    elif china_str == "湖北":
        return "Hubei"
    elif china_str == "湖南":
        return "Hunan"
    elif china_str == "黑龙江":
        return "Heilongjiang"
    elif china_str == "吉林":
        return "Jilin"
    elif china_str == "辽宁":
        return "Liaoning"
    elif china_str == "甘肃":
        return "Gansu"
    elif china_str == "内蒙古":
        return "Inner Mongolia"
    elif china_str == "宁夏":
        return "Ningxia"
    elif china_str == "青海":
        return "Qinghai"
    elif china_str == "陕西":
        return "Shaanxi"
    elif china_str == "新疆":
        return "Xinjiang"
    elif china_str == "重庆":
        return "Chongqing"
    elif china_str == "四川":
        return "Sichuan"
    elif china_str == "西藏":
        return "Tibet"
    elif china_str == "云南":
        return "Yunnan"
    else:
        return "address_error"

def judge(mark_num): # 从标号返回城市
    mark={
    'STN80000A':'北京',
    'STN80000B':'北京',
    'STN80000C':'北京',
    'STN80006A':'北京',
    'STN80006B':'北京',
    'STN80006C':'北京',
    'STN80006D':'北京',
    'STN80006E':'北京',
    'STN80006F':'北京',
    'STN80006G':'北京',
    'STN80006H':'北京',
    'STN80006K':'北京',
    'STN80006L':'北京',
    'STN80006M':'北京',
    'STN80006N':'北京',
    'STN80006P':'北京',
    'STN80006Q':'北京',
    'STN80031A':'北京',
    'STN80031B':'北京',
    'STN80031C':'北京',
    'STN80031D':'北京',
    'STN80033A':'北京',
    'STN80033B':'北京',
    'STN80033C':'北京',
    'STN80033D':'北京',
    'STN80033E':'北京',
    'STN80033F':'北京',
    'STN80033G':'北京',
    'STN80034A':'北京',
    'STN80034B':'北京',
    'STN80034C':'北京',
    'STN80034D':'北京',
    'STN80034E':'北京',
    'STN80034F':'北京',
    'STN80034G':'北京',
    'STN80038A':'北京',
    'STN80038B':'北京',
    'STN80038C':'北京',
    'STN80042A':'北京',
    'STN80043A':'北京',
    'STN80046A':'北京',
    'STN80055A':'北京',
    'STN80055B':'北京',
    'STN80055C':'北京',
    'STN80055D':'北京',
    'STN80055E':'北京',
    'STN80058A':'北京',
    'STN80058B':'北京',
    'STN80058C':'北京',
    'STN80058D':'北京',
    'STN80067A':'北京',
    'STN80067B':'北京',
    'STN80067C':'北京',
    'STN80067D':'北京',
    'STN80068A':'北京',
    'STN80068B':'北京',
    'STN80068C':'北京',
    'STN80069A':'北京',
    'STN80069B':'北京',
    'STN80080A':'北京',
    'STN80082A':'北京',
    'STN80082B':'北京',
    'STN80082C':'北京',
    'STN80084A':'北京',
    'STN80084B':'北京',
    'STN80084C':'北京',
    'STN80084D':'北京',
    'STN80089A':'北京',
    'STN80089B':'北京',
    'STN80089C':'北京',
    'STN80089D':'北京',
    'STN80089E':'北京',
    'STN80089F':'北京',
    'STN80091A':'北京',
    'STN80091B':'北京',
    'STN80091C':'北京',
    'STN80092A':'北京',
    'STN80092B':'北京',
    'STN80092C':'北京',
    'STN80092D':'北京',
    'STN80096A':'北京',
    'STN80097A':'北京',
    'STN80097B':'北京',
    'STN80098A':'北京',
    'STN80099A':'北京',
    'STN80099B':'北京',
    'STN80102A':'北京',
    'STN80102B':'北京',
    'STN80110A':'北京',
    'STN80110B':'北京',
    'STN80111A':'北京',
    'STN80111B':'北京',
    'STN80116A':'北京',
    'STN80116B':'北京',
    'STN80118A':'北京',
    'STN80120A':'北京',
    'STN80120B':'北京',
    'STN80120C':'北京',
    'STN80120D':'北京',
    'STN80123A':'北京',
    'STN80123B':'北京',
    'STN80130A':'北京',
    'STN80130B':'北京',
    'STN80132A':'北京',
    'STN80132B':'北京',
    'STN80132C':'北京',
    'STN80024A':'长春',
    'STN80024B':'长春',
    'STN80024C':'长春',
    'STN80024D':'长春',
    'STN80024E':'长春',
    'STN80024F':'长春',
    'STN80113A':'长春',
    'STN80113B':'长春',
    'STN80129A':'长春',
    'STN80129B':'长春',
    'STN80134A':'长春',
    'STN80134B':'长春',
    'STN80134C':'长春',
    'STN80134D':'长春',
    'STN80134E':'长春',
    'STN80134F':'长春',
    'STN80134G':'长春',
    'STN80134H':'长春',
    'STN80134I':'长春',
    'STN80027A':'长沙',
    'STN80027B':'长沙',
    'STN80027C':'长沙',
    'STN80125A':'长沙',
    'STN80125B':'长沙',
    'STN80125C':'长沙',
    'STN80125D':'长沙',
    'STN80036A':'成都',
    'STN80051A':'成都',
    'STN80066A':'成都',
    'STN80119A':'成都',
    'STN80119B':'成都',
    'STN80119C':'成都',
    'STN80119D':'成都',
    'STN80122A':'成都',
    'STN80122B':'成都',
    'STN80003A':'大连',
    'STN80047A':'大连',
    'STN80052A':'大连',
    'STN80073A':'福州',
    'STN80005A':'广州',
    'STN80005B':'广州',
    'STN80005C':'广州',
    'STN80005D':'广州',
    'STN80005E':'广州',
    'STN80005F':'广州',
    'STN80005G':'广州',
    'STN80005H':'广州',
    'STN80005I':'广州',
    'STN80005J':'广州',
    'STN80005K':'广州',
    'STN80005L':'广州',
    'STN80005M':'广州',
    'STN80035A':'广州',
    'STN80077A':'广州',
    'STN80077B':'广州',
    'STN80077C':'广州',
    'STN80007A':'哈尔滨',
    'STN80030A':'海口',
    'STN80018A':'杭州',
    'STN80040A':'杭州',
    'STN80040B':'杭州',
    'STN80040C':'杭州',
    'STN80040D':'杭州',
    'STN80040E':'杭州',
    'STN80040F':'杭州',
    'STN80041A':'杭州',
    'STN80041B':'杭州',
    'STN80041C':'杭州',
    'STN80041D':'杭州',
    'STN80041E':'杭州',
    'STN80041F':'杭州',
    'STN80041G':'杭州',
    'STN80041H':'杭州',
    'STN80041J':'杭州',
    'STN80041L':'杭州',
    'STN80041M':'杭州',
    'STN80008A':'合肥',
    'STN80008B':'合肥',
    'STN80008C':'合肥',
    'STN80008D':'合肥',
    'STN80064A':'呼和浩特',
    'STN80064B':'呼和浩特',
    'STN80011A':'济南',
    'STN80011B':'济南',
    'STN80011C':'济南',
    'STN80011D':'济南',
    'STN80105A':'济南',
    'STN80105B':'济南',
    'STN80141A':'济南',
    'STN80141B':'济南',
    'STN80141C':'济南',
    'STN80133A':'开封',
    'STN80133B':'开封',
    'STN80133C':'开封',
    'STN80133D':'开封',
    'STN80012A':'昆明',
    'STN80121A':'昆明',
    'STN80013A':'兰州',
    'STN80013B':'兰州',
    'STN80131A':'兰州',
    'STN80131B':'兰州',
    'STN80131C':'兰州',
    'STN80094A':'临沂',
    'STN80062A':'洛阳',
    'STN80135A':'绵阳',
    'STN80135B':'绵阳',
    'STN80015A':'南昌',
    'STN80083A':'南昌',
    'STN80090A':'南昌',
    'STN80090B':'南昌',
    'STN80090C':'南昌',
    'STN80014A':'南京',
    'STN80014B':'南京',
    'STN80014C':'南京',
    'STN80044A':'南京',
    'STN80044B':'南京',
    'STN80044C':'南京',
    'STN80044D':'南京',
    'STN80049A':'南京',
    'STN80049B':'南京',
    'STN80049C':'南京',
    'STN80049D':'南京',
    'STN80049E':'南京',
    'STN80049F':'南京',
    'STN80075A':'南京',
    'STN80075B':'南京',
    'STN80075C':'南京',
    'STN80075D':'南京',
    'STN80076A':'南京',
    'STN80106A':'南京',
    'STN80106B':'南京',
    'STN80106C':'南京',
    'STN80106D':'南京',
    'STN80106E':'南京',
    'STN80010A':'南宁',
    'STN80085A':'南通',
    'STN80085B':'南通',
    'STN80085C':'南通',
    'STN80059A':'宁波',
    'STN80059B':'宁波',
    'STN80059C':'宁波',
    'STN80059D':'宁波',
    'STN80059E':'宁波',
    'STN80059F':'宁波',
    'STN80137A':'宁波',
    'STN80137B':'宁波',
    'STN80023A':'青岛',
    'STN80023B':'青岛',
    'STN80101A':'汕头',
    'STN80101B':'汕头',
    'STN80016A':'上海',
    'STN80016B':'上海',
    'STN80017A':'上海',
    'STN80017B':'上海',
    'STN80039A':'上海',
    'STN80039B':'上海',
    'STN80039C':'上海',
    'STN80054A':'上海',
    'STN80054B':'上海',
    'STN80054C':'上海',
    'STN80054D':'上海',
    'STN80054E':'上海',
    'STN80056A':'上海',
    'STN80056B':'上海',
    'STN80056C':'上海',
    'STN80079A':'上海',
    'STN80081A':'上海',
    'STN80081B':'上海',
    'STN80100A':'上海',
    'STN80100B':'上海',
    'STN80104A':'上海',
    'STN80104B':'上海',
    'STN80104C':'上海',
    'STN80104D':'上海',
    'STN80104E':'上海',
    'STN80104F':'上海',
    'STN80138A':'上海',
    'STN80138B':'上海',
    'STN80138C':'上海',
    'STN80138D':'上海',
    'STN80138E':'上海',
    'STN80022A':'深圳',
    'STN80045A':'深圳',
    'STN80045B':'深圳',
    'STN80045C':'深圳',
    'STN80045D':'深圳',
    'STN80065A':'深圳',
    'STN80065B':'深圳',
    'STN80071A':'沈阳',
    'STN80071B':'沈阳',
    'STN80071C':'沈阳',
    'STN80071D':'沈阳',
    'STN80078A':'沈阳',
    'STN80078B':'沈阳',
    'STN80078C':'沈阳',
    'STN80009A':'石家庄',
    'STN80009B':'石家庄',
    'STN80053A':'石家庄',
    'STN80053B':'石家庄',
    'STN80053C':'石家庄',
    'STN80053D':'石家庄',
    'STN80139A':'石家庄',
    'STN80139B':'石家庄',
    'STN80050A':'苏州',
    'STN80050B':'苏州',
    'STN80050C':'苏州',
    'STN80050D':'苏州',
    'STN80050E':'苏州',
    'STN80112A':'苏州',
    'STN80112B':'苏州',
    'STN80112C':'苏州',
    'STN80112D':'苏州',
    'STN80112E':'苏州',
    'STN80112F':'苏州',
    'STN80108A':'太仓',
    'STN80108B':'太仓',
    'STN80026A':'太原',
    'STN80026B':'太原',
    'STN80127A':'太原',
    'STN80127B':'太原',
    'STN80136A':'太原',
    'STN80136B':'太原',
    'STN80019A':'天津',
    'STN80019B':'天津',
    'STN80029A':'天津',
    'STN80029B':'天津',
    'STN80029C':'天津',
    'STN80048A':'天津',
    'STN80048B':'天津',
    'STN80057A':'天津',
    'STN80057B':'天津',
    'STN80074A':'威海',
    'STN80074B':'威海',
    'STN80070A':'潍坊',
    'STN80070B':'潍坊',
    'STN80070C':'潍坊',
    'STN80070D':'潍坊',
    'STN80037A':'乌鲁木齐',
    'STN80020A':'武汉',
    'STN80020B':'武汉',
    'STN80020C':'武汉',
    'STN80021A':'武汉',
    'STN80021B':'武汉',
    'STN80021C':'武汉',
    'STN80103A':'武汉',
    'STN80103B':'武汉',
    'STN80128A':'武汉',
    'STN80128B':'武汉',
    'STN80028A':'西安',
    'STN80115A':'西安',
    'STN80117A':'西安',
    'STN80117B':'西安',
    'STN80117C':'西安',
    'STN80117D':'西安',
    'STN80117E':'西安',
    'STN80117F':'西安',
    'STN80025A':'厦门',
    'STN80025B':'厦门',
    'STN80025C':'厦门',
    'STN80025D':'厦门',
    'STN80025E':'厦门',
    'STN80025F':'厦门',
    'STN80126A':'烟台',
    'STN80109A':'延吉',
    'STN80109B':'延吉',
    'STN80086A':'扬州',
    'STN80086B':'扬州',
    'STN80086C':'扬州',
    'STN80086D':'扬州',
    'STN80086E':'扬州',
    'STN80072A':'郑州',
    'STN80072B':'郑州',
    'STN80072C':'郑州',
    'STN80072D':'郑州',
    'STN80001A':'重庆',
    'STN80001B':'重庆',
    'STN80060A':'重庆',
    'STN80060B':'重庆',
    'STN80107A':'重庆',
    'STN80107B':'重庆',
    'STN80107C':'重庆'
        }

    return mark[mark_num]

def headers_all(Cookie_str): # 返回所有headers
    headers = {
    "header_yz_login" :
        {
        'Accept':'image/webp,image/*,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Connection':'keep-alive',
        'Cookie': Cookie_str,
        'Host':'toefl.etest.net.cn',
        'Referer':'https://toefl.etest.net.cn/cn/',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        },

    "headers_login" :
        {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Cookie': Cookie_str,
        'Host':'toefl.etest.net.cn',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        },

    "headers_query" : 
        {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': Cookie_str,
        'Host': 'toefl.etest.net.cn',
        'Referer': 'https://toefl.etest.net.cn/cn/MyHome/?',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        },
    "headers_result" :
        {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': Cookie_str,
        'Host': 'toefl.etest.net.cn',
        'Referer': 'https://toefl.etest.net.cn/cn/Information?page=SeatsQuery',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        },
    "headers_myhome" :
        {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': Cookie_str,
        'Host': 'toefl.etest.net.cn',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        },
    "headers_admintable" :
        {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': Cookie_str,
        'Host': 'toefl.etest.net.cn',
        'Referer': "https://toefl.etest.net.cn/cn/MyHome/?",
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        },
    "headers_seatsquery" :
        {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': Cookie_str,
        'Host': 'toefl.etest.net.cn',
        'Referer': "https://toefl.etest.net.cn/cn/CityAdminTable",
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        },
            }
    return headers

def deal_with_time(time_date):
    timedate = time_date.split(" ")[0].replace("年","-").replace("月","-").replace("日","")
    temp_list = timedate.split("-")
    if len(temp_list[1]) == 1:
        temp_list[1] = "0" + temp_list[1]
    if len(temp_list[2]) == 1:
        temp_list[2] = "0" + temp_list[2]
    timedate = "-".join(temp_list)
    return timedate

def time2china_time(time_temp):
    time_list = time_temp.split("-")
    if time_list[1][0] == "0":
        time_list[1] = time_list[1].replace("0","")
    if time_list[2][0] == "0":
        time_list[2] = time_list[2].replace("0","")
    time_temp = "-".join(time_list)
    time_temp = time_temp.replace("-","年",1).replace("-","月",1) + "日"
    return time_temp

















# def get_ip():
#     global q
#     q = Queue.Queue()
#     # {"code":0,
#     # "success":"true",
#     #"msg":"",
#     # "data":[{"IP":"113.244.57.198:37548","ExpireTime":"2018-04-12 11:58:20"},{"IP":"115.55.208.70:37724","ExpireTime":"2018-04-12 11:58:20"}]}
#     ip_dic_str = requests.get("http://120.25.150.39:8081/index.php/api/entry?method=proxyServer.generate_api_url&packid=&fa=&qty=2&time=1&pro=&city=&port=1&format=json&ss=6&css=%2C&ipport=1&dt=1").content
#     ip_dic = json.loads(ip_dic_str)
#     ip_list = ip_dic["data"]
#     for ip in ip_list:
#         ip = ip['IP']
#         q.put(ip)

    # return q
# def get_mip():
#     global q
#     q = Queue.Queue()
#     # {"code":0,
#     # "success":"true",
#     #"msg":"",
#     # "data":[{"IP":"113.244.57.198:37548","ExpireTime":"2018-04-12 11:58:20"},{"IP":"115.55.208.70:37724","ExpireTime":"2018-04-12 11:58:20"}]}
#     ip_dic_str = requests.get("http://120.25.150.39:8081/index.php/api/entry?method=proxyServer.generate_api_url&packid=&fa=&qty=52&time=1&pro=%E5%8C%97%E4%BA%AC%E7%9B%B4%E8%BE%96%E5%B8%82&city=%E5%8C%97%E4%BA%AC%E5%B8%82&port=1&format=json&ss=1&css=&ipport=1&dt=0").content
#     ip_dic = json.loads(ip_dic_str)
#     ip_list = ip_dic["data"]
#     for ip in ip_list:
#         ip = ip['IP']
#         try:  
#             requests.get('http://toefl.etest.net.cn/cn/', proxies={"http":"http://%s"%ip})  
#         except:  
#             print 'connect failed'  
#         else:   
#             q.put(ip)

#     return q


  
# for section in section_list[1:]:
#                 temp_set = []
                
#                 time_d = re.findall(r'<td.*?><b>(.*?)</b></td>',section,re.S)
#                 if time_d != []:
#                     timedate = time_d[0]                    
#                 aim_list = re.findall(r'<tr bgcolor="#CCCCCC">(.*?)</tr>', section, re.S)
#                 for aim in aim_list:
#                     aim_clear = re.findall(r'<td.*?>(.*?)</td>', aim, re.S)
#                     if "有名额" in aim_clear:
#                         temp_set.append(judge(aim_clear[1]))
#                         print(temp_set)
#                         self.mongo.handle_yes(timedate, aim_clear)
#                         aim_clear[0] = (timedate + area_str)
#                         aim_clear = " ".join(aim_clear)
#                         with open('data.txt',"r") as f_read:
#                             lines = f_read.read()
#                             if aim_clear not in lines:
#                                 f_data.write("%s \n"%aim_clear)
#                                 with open("new_data.txt","a") as f_new:
#                                     res_list.append(aim_clear)
#                                     now = time.strftime('%Y-%m-%d ',time.localtime(time.time()))
#                                     f_new.write("%s新放出的考位%s \n"%(now, aim_clear))
#                     else:
#                         print(temp_set)
#                         if judge(aim_clear[1]) not in temp_set:
#                             self.mongo.handle_no(timedate, aim_clear)
#             print("%s考位查询完毕"%address)
#             return res_list
#    