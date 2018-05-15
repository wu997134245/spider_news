# coding=utf-8
import requests

def login(username,password):
    sid = requests.session()
    login_url = "http://www.yicaitop.com/dede/login.php"
    sid.get(login_url)
    params = {"gotopage": "/dede/","dopost": "login","adminstyle":"newdedecms","userid": username,"pwd": password,"sm1":""}
    sid.post(login_url, data=params)
    return sid

username = "admin"
password = "admin666888"

sid = login(username,password)
# url = "http://www.yicaitop.com/dede/article_add.php"
# params = {
# "channelid": (None, "1"),
# "dopost": (None, "save"),
# "title": (None, "testautologin"),
# "shorttitle": (None, "abcd1234"),
# "tags": (None, "abcd1234"),
# "typeid": (None, "4"),
# "description": (None, "test"),
# "body": (None, "test"),
# "autokey": (None, "1"),
# }
# res = sid.post(url, files=params)
# print res.request.body
# print res.request.headers

type_map = {
 "分析": "4", 
 "娱乐": "11", 
 "股票基金": "1", 
 "入门": "35", 
 "综述": "14", 
 "科技中心": "38", 
 "档案": "31", 
 "生活": "40", 
 "银行保险": "16", 
 "政策": "17", 
 "快讯": "10", 
 "精选": "8", 
 "最新": "41", 
 "期货": "53", 
 "排名": "33", 
 "要闻": "3", 
 "数据": "13", 
 "市场": "6", 
 "商业": "24", 
 "网贷理财": "29", 
 "数码": "39", 
 "舆情": "34", 
 "投资": "25", 
 "房产": "26", 
 "活动": "32", 
 "理财知识": "23", 
 "热点推荐": "54", 
 "案例": "19", 
 "新闻": "9", 
 "平台": "30", 
 "汽车": "27", 
 "互联网": "42", 
 "讲解": "12", 
 "新闻热点": "7", 
 "动态": "2", 
 "指南": "18"
}