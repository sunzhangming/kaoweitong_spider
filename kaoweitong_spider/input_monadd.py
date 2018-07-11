from redis import *
import time
sr = StrictRedis(host='localhost', port=6379, db=0)



now = time.strftime('%Y%m',time.localtime(time.time()))
now = "201805"
month_address_list = sr.smembers("month_address")
for month_address in month_address_list:
    month_temp = month_address.decode().split(",")[0]
    if month_temp < now:
        sr.srem("month_address",month_address)

if now[4:] == "12":
    month = now
else:
    month = str(int(now) + 1)


address_list = ["Beijing", "Hebei", "Shanxi", "Tianjin", "Anhui","Fujian", "Jiangsu", "Jiangxi", "Shandong", "Shanghai", "Zhejiang", "Guangdong", "Guangxi", "Guizhou", "Hainan","Henan", "Hubei", "Hunan","Heilongjiang", "Jilin", "Liaoning", "Gansu", "Inner Mongolia", "Ningxia", "Qinghai", "Shaanxi", "Xinjiang", "Chongqing" ,"Sichuan", "Tibet", "Yunnan"]

for address in address_list:
    value = "%s,%s"%(month, address)
    sr.sadd("month_address",value)

for address in address_list:
    value = "%s,%s"%(now, address)
    sr.sadd("month_address",value)

