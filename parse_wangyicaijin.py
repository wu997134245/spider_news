# coding=utf-8
import random

import requests
import time
from bs4 import BeautifulSoup
import random
import re
import time
import datetime
import requests
import json
import cPickle as p
from log import parse_log
import os

current_path = os.path.dirname(os.path.realpath(__file__))
today_date =  datetime.datetime.now().date().strftime('/%m%d/')





url_base = 'http://money.163.com/'

url_wenzhang = 'http://finance.sina.com.cn/stock/usstock/c/2018-04-10/doc-ifyvtmxe7675230.shtml'
#cookies = {'_identity':'14b78da3fc25c229cec53847a275afa2c17c0c22f061fb8f4ab3d1e20a9278dfa%3A2%3A%7Bi%3A0%3Bs%3A9%3A%22_identity%22%3Bi%3A1%3Bs%3A46%3A%22%5B8%2C%22eUkGP7jGNhmsqZWZbABDesm8htrFy6kN%22%2C2592000%5D%22%3B%7D'}




headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate',
'Accept-Language':'zh-CN,zh;q=0.9',
'Cache-Control':'no-cache',
'Connection':'keep-alive',
'Host':'money.163.com',
'Pragma':'no-cache',
'Upgrade-Insecure-Requests':'1',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36'
               }


def get_data(url = url_base):
    r = requests.get(url, headers=headers)
    return r.content



def post_data(url,params):
    r = requests.post(url, headers=headers,params=params)
    return r.content




def find_data(url):
    #获取导航栏URL
    html = get_data(url)
    soup = BeautifulSoup(html, "html.parser")
    try:
        nav = soup.find('div',class_ = 'nav common_wrap')
    except:
        return []
    li = nav.find_all('a')
    parse_log.debug(li)
    nav_url = []
    parse_log.debug(nav_url)
    filter_list = [u'行情', u'大盘', u'净值', u'评论', u'百科', u'博客', u'专题',u'滚动',u'港股']
    for i in li:
        if i.text in filter_list:
            continue
        parse_log.debug('u\'' + i.text + '\''+ ':' + '\'\'' + ',')
        nav_url.append({'type_name':i.text,'type_url':i['href']})

    parse_log.debug(nav_url)
    return nav_url



def get_page(url):
    #获取文章URL链接,获取当日文章
    column_url = url
    article_list = []

    def get_rules_page_1():
        html = get_data(column_url)
        soup = BeautifulSoup(html, "html.parser")
        a = soup.find_all('a')
        for i in a:
            try:
                wenzhang_url = i['href']
            except:
                continue
            search_obj = re.search(r'http://.+{0}.+?html'.format(today_date), wenzhang_url)
            if not search_obj:
                continue
            article_list.append(wenzhang_url)


    def get_rules_more():

        data = get_data('http://money.163.com/special/002557S5/newsdata_idx_index.js?callback=data_callback')
        data = str(data.lstrip('data_callback').strip('()'))
        html = json.loads(data)
        for i in html:
            wenzhang_url = i['docurl']
            search_obj = re.search(r'http://{0}.+?html'.format(today_date), wenzhang_url)
            if not search_obj:
                continue
            article_list.append(wenzhang_url)

    get_rules_page_1()
    #get_rules_more()
    #article_list = list(set(article_list))
    parse_log.debug(article_list)
    return len(article_list),article_list



def get_url_rules_3(url):
    #获取文章URL链接,获取当日文章
    column_url = url
    page_num = 2
    article_list = []


    def get_rules_more(page_num):
        'http://money.163.com/special/00252G50/macro_02.html'
        html = get_data(column_url)
        added_url = 0
        soup = BeautifulSoup(html, "html.parser")
        a_list_div = soup.find('div',class_='col_l')
        a = a_list_div.find_all('a')
        for i in a:
            try:
                wenzhang_url = i['href']
            except:
                continue
            search_obj = re.search(r'http://.+{0}.+?html'.format(today_date), wenzhang_url)
            if not search_obj:
                continue
            article_list.append(wenzhang_url)
            added_url +=1

        if added_url:
            column_url_ = column_url.rstrip('.html') + '_' + '%02d' % page_num + '.html'
            return 1
        else:
            return 0


    while True:
        status = get_rules_more(page_num)
        if status:
            page_num+=1
        else:
            break


    parse_log.debug(article_list)
    return len(article_list),article_list


def get_url_rules_2(url):
    #获取文章URL链接,获取当日文章
    column_url = url
    page_num = 2
    article_list = []


    html = get_data(column_url)
    added_url = 0
    soup = BeautifulSoup(html, "html.parser")
    a_list_div = soup.find('div',class_='col_l')
    a = a_list_div.find_all('a')
    for i in a:
        try:
            wenzhang_url = i['href']
        except:
            continue
        search_obj = re.search(r'http://.+{0}.+?html'.format(today_date), wenzhang_url)
        if not search_obj:
            continue
        article_list.append(wenzhang_url)

    parse_log.debug(article_list)
    return len(article_list),article_list




def get_hjbk_page(url):
    #获取文章URL链接,获取当日文章
    column_url = url + '/page'
    page_num = 1
    article_list = []

    def get_url(page_num):
        html = json.loads(post_data(column_url,{'page':page_num}))['data']
        added_url = 0
        for i in html:
            try:
                wenzhang_url = i['NewsID']
            except:
                continue
            search_obj = re.search(r'{0}.+?'.format(today_date), wenzhang_url)
            if not search_obj:
                continue
            wenzhang_url = url_base + '/C/' + wenzhang_url[:8] + "/" + wenzhang_url + ".html"
            article_list.append(wenzhang_url)
            added_url +=1

        if added_url == len(html):
            return 1
        else:
            return 0


    while True:
        status = get_url(page_num)
        if status:
            page_num+=1
        else:
            break
    parse_log.debug(article_list)
    return len(article_list),article_list





def handle_article(url):
    #处理文章内容,提取标题和正文
    #处理广告,跳转链接
    try:
        html = get_data(url).decode('gbk').encode('utf8')
    except:
        html = get_data(url)
    soup = BeautifulSoup(html, "html.parser").find('div',class_='post_content_main')

    try:
        article_title = soup.find_all('h1')[0].text
    except:
        article_title=''

    try:
        artibody = soup.find_all('div',class_='post_text')[0]
    except:
        artibody=''

    try:
        advertising = soup.find_all('div',class_='hqimg_related')[0]
        advertising.extract()
    except:
        pass

    try:
        a_tag = soup.find_all('a')
        for i in a_tag:
            del i['href']
    except:
        pass

    #parse_log.debug() article_title,artibody
    return article_title,artibody




handle_article_CMDs={
u'首页':handle_article,
u'宏观':handle_article,
u'国际':handle_article,
u'股票':handle_article,
u'新股':handle_article,
u'美股':handle_article,
u'期货':handle_article,
u'比特币':handle_article,
u'商业':handle_article,
u'产经':handle_article,
u'能源':handle_article,
u'交通':handle_article,
u'房产':handle_article,
u'汽车':handle_article,
u'商贸':handle_article,
u'金融':handle_article,
u'理财':handle_article,
u'基金':handle_article,}


get_article_CMDs ={
u'首页':get_page,
u'宏观':get_url_rules_2,
u'国际':get_url_rules_2,
u'股票':get_page,
u'新股':get_page,
u'美股':get_page,
u'期货':get_page,
u'比特币':get_page,
u'商业':get_page,
u'产经':get_page,
u'能源':get_url_rules_2,
u'交通':get_url_rules_2,
u'房产':get_url_rules_2,
u'汽车':get_url_rules_2,
u'商贸':get_url_rules_2,
u'金融':get_page,
u'理财':get_page,
u'基金':get_page,
}


def upload(article_title,artibody,upload_type):
    #上传文章到后台
    #article_title, artibody = handle_article(url)
    if not artibody or not article_title:
       return {'status':0,'msg':u'失败'}
    backend_url = "http://www.yicaitop.com/dede/article_add.php"
    this_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    params = {
        "channelid": (None, "1"),
        "dopost": (None, "save"),
        "title": (None, article_title),
        "shorttitle": (None, article_title),
        "tags": (None, article_title),
        "typeid": (None, upload_type),
        "body": (None, str(artibody)),
        "autokey": (None, "1"),
        "ishtml": (None, "1"),
        "remote":(None,'1'),
        "pubdate": (None, this_time),
    }

    #sid.post(backend_url,params)

    return {'status':1,'msg':u'成功'}


def get_all_article():

    article = []
    nav_url = find_data(url_base)
    article_num = 0
    article_list = []
    # nav_url.append(url_base)
    parse_log.info('开始爬取当日所有文章链接....')
    for i in nav_url:
        #遍历导航栏链接
        page_num, art_list = get_article_CMDs[i['type_name']](i['type_url'])
        if not page_num:
            #去除没有文章的分类
            continue
        parse_log.debug(u'已获取{1}文章链接{0}条'.format(page_num,i['type_name'] ))
        article_list.append({'type_name':i['type_name'],'art_list':art_list})




    total = 0
    upload_end = []

    for i in article_list:
        #upload_type = news_type[i['type_name']]
        waiting_upload = i['art_list']
        parse_log.debug('开始上传,待上传{0}条'.format(len(waiting_upload)))
        total = total + len(waiting_upload)

        for a in waiting_upload:
            if a not in upload_end:
                article_title, artibody = handle_article_CMDs[i['type_name']](a)
                if not artibody or not article_title:
                    continue
                article.append({'title': article_title, 'body': artibody, 'type': i['type_name'], 'url': a,'source_url': url_base})
                parse_log.debug(u'获取文章:{0} 栏目.....{1}/{2}.........{3}'.format(i['type_name'], waiting_upload.index(a),
                                                                        len(waiting_upload), a))
                upload_end.append(a)
            else:
                parse_log.debug('已存在')
                continue
    parse_log.info('已获取文章{0}条'.format(len(article)))
    return article



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





if __name__ == '__main__':
    get_all_article()
    #handle_article(url_wenzhang)
    #upload()